# tests/test_ai_recommendations.py

import json
from unittest.mock import MagicMock

import pytest
from botocore.exceptions import ClientError

from src.aws.bedrock import get_ai_recommendations
from src.shared_models import SimulationParameters

# A constant for a standard, successful response from the Bedrock mock
MOCK_SUCCESS_BODY = json.dumps(
    {
        "results": [
            {
                "outputText": """[
            {"recommendation": "Mocked: Open Gates C and D", "reason": "Mocked: Reduces congestion."},
            {"recommendation": "Mocked: Deploy 20 staff members", "reason": "Mocked: Guides attendees."}
        ]"""
            }
        ]
    }
)


@pytest.fixture
def mock_boto3_client(mocker):
    """A targeted mock fixture that patches the bedrock_runtime_client where it's used."""
    mock_client = mocker.patch("src.aws.bedrock.bedrock_runtime_client")

    # Configure a default successful response
    mock_response_stream = MagicMock()
    mock_response_stream.read.return_value = MOCK_SUCCESS_BODY
    mock_client.invoke_model.return_value = {"body": mock_response_stream}

    return mock_client


# === Test Cases ===


def test_get_ai_recommendations_successful_json(mock_boto3_client):
    """Tests the happy path: a successful API call with valid JSON."""
    # Arrange
    params = SimulationParameters(attendees=10000, open_gates=3, optimization_goal="Maximum Safety")

    # Act
    recommendations = get_ai_recommendations(params)

    # Assert
    assert len(recommendations) == 2
    assert recommendations[0].recommendation == "Mocked: Open Gates C and D"
    assert recommendations[1].reason == "Mocked: Guides attendees."
    mock_boto3_client.invoke_model.assert_called_once()


def test_get_ai_recommendations_falls_back_on_invalid_json(mock_boto3_client):
    """Tests that the function falls back to mock data if the API returns malformed JSON."""
    # Arrange
    params = SimulationParameters(attendees=10000, open_gates=3, optimization_goal="Maximum Safety")
    invalid_json_body = json.dumps({"results": [{"outputText": "This is not valid JSON."}]})
    mock_response_stream = MagicMock()
    mock_response_stream.read.return_value = invalid_json_body
    mock_boto3_client.invoke_model.return_value = {"body": mock_response_stream}

    # Act
    recommendations = get_ai_recommendations(params)

    # Assert: The function should fall back to the built-in mock data
    assert len(recommendations) > 0
    assert "Mock" not in recommendations[0].recommendation  # Ensure it's not the test's mock


def test_get_ai_recommendations_falls_back_on_client_error(mock_boto3_client):
    """Tests that the function falls back to mock data on an AWS ClientError."""
    # Arrange
    params = SimulationParameters(attendees=10000, open_gates=3, optimization_goal="Maximum Safety")
    mock_boto3_client.invoke_model.side_effect = ClientError(
        error_response={"Error": {"Code": "AccessDenied", "Message": "Access denied"}},
        operation_name="InvokeModel",
    )

    # Act
    recommendations = get_ai_recommendations(params)

    # Assert: The function should fall back to the built-in mock data
    assert len(recommendations) > 0
    assert "Mock" not in recommendations[0].recommendation


@pytest.mark.parametrize(
    "goal, expected_phrase",
    [
        ("Maximum Safety", "MAXIMIZE SAFETY"),
        ("Balanced Safety & Cost", "BALANCE SAFETY IMPROVEMENTS with COST EFFICIENCY"),
    ],
)
def test_prompt_contains_correct_goal_phrasing(mock_boto3_client, goal, expected_phrase):
    """Tests that the correct phrasing is in the prompt for each optimization goal."""
    # Arrange
    params = SimulationParameters(attendees=5000, open_gates=2, optimization_goal=goal)

    # Act
    get_ai_recommendations(params)

    # Assert: Check the content of the prompt that was sent to the model
    mock_boto3_client.invoke_model.assert_called_once()
    call_kwargs = mock_boto3_client.invoke_model.call_args.kwargs
    request_body = json.loads(call_kwargs["body"])
    prompt = request_body["inputText"]

    assert expected_phrase in prompt
