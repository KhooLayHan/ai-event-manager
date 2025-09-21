# tests/test_ai_recommendations.py

import json
from unittest.mock import MagicMock, patch

import pytest
from botocore.exceptions import ClientError

from src.aws.bedrock import get_ai_recommendations
from src.shared_models import AIRecommendation, SimulationParameters

# This is a constant we can reuse in our tests
MOCK_SUCCESS_RESPONSE_BODY = json.dumps(
    {
        "results": [
            {
                "outputText": """[
            {"recommendation": "Open Gates C and D", "reason": "Distributing entry points reduces congestion."},
            {"recommendation": "Deploy 20 staff members", "reason": "Additional staff can guide attendees."}
        ]"""
            }
        ]
    }
)


@pytest.fixture
def valid_params():
    """Fixture for valid simulation parameters."""
    return SimulationParameters(
        attendees=10000,
        open_gates=3,
        optimization_goal="Maximum Safety",
    )


@pytest.fixture
def mock_bedrock_client():
    """
    Mock Bedrock client fixture for testing.
    """

    with patch("src.aws.bedrock.bedrock_runtime_client") as mock_client:
        # Configure the invoke_model method to return a successful mock response
        mock_response = MagicMock()
        mock_response["body"] = MagicMock()
        mock_response.invoke_model.return_value = """
        {
            "results": [
            {
                "outputText": "[{\"recommendation\": \"Test Recommendation\", \"reason\": \"Test Reason\"}]"
            }
            ]
        }
            """

        # Configure the client factory to return our mock
        mock_client.invoke_model.return_value = mock_response
        yield mock_client


@pytest.fixture
def mock_boto3_client(mocker):
    """
    A more targeted mock that patches the boto3.client call within the bedrock module.
    This is a more robust way to mock.
    """
    # Patch the specific client instance used in your bedrock.py file
    mock_client = mocker.patch("src.aws.bedrock.bedrock_runtime_client")
    return mock_client


def test_get_ai_recommendations_successful_json(mock_boto3_client, valid_params):
    """Test successful retrieval of AI recommendations with valid JSON response."""
    # Arrange: Configure the mock to return a successful response
    mock_response_stream = MagicMock()
    mock_response_stream.read.return_value = MOCK_SUCCESS_RESPONSE_BODY
    mock_boto3_client.invoke_model.return_value = {"body": mock_response_stream}

    # Act: Call the function
    recommendations = get_ai_recommendations(valid_params)

    # Assert: Check the results
    assert len(recommendations) == 2
    assert recommendations[0].recommendation == "Open Gates C and D"
    assert recommendations[1].reason == "Additional staff can guide attendees."
    mock_boto3_client.invoke_model.assert_called_once()  # Verify the mock was called


def test_get_ai_recommendations_invalid_json(mock_boto3_client, valid_params):
    """Test handling of invalid JSON response from Bedrock."""
    # Arrange: Configure the mock to return an invalid JSON string
    invalid_json_body = json.dumps({"results": [{"outputText": "This is not valid JSON."}]})
    mock_response_stream = MagicMock()
    mock_response_stream.read.return_value = invalid_json_body
    mock_boto3_client.invoke_model.return_value = {"body": mock_response_stream}

    # Act: Call the function
    recommendations = get_ai_recommendations(valid_params)

    # Assert: The function should fall back to mock data
    assert len(recommendations) > 0
    assert recommendations[0].recommendation is not None  # Basic check for mock data structure


def test_get_ai_recommendations_client_error(mock_boto3_client, valid_params):
    """Test handling of a ClientError from the AWS service."""
    # Arrange: Configure the mock to raise a ClientError
    mock_boto3_client.invoke_model.side_effect = ClientError(
        error_response={"Error": {"Code": "AccessDenied", "Message": "Access denied"}},
        operation_name="InvokeModel",
    )

    # Act: Call the function
    recommendations = get_ai_recommendations(valid_params)

    # Assert: The function should fall back to mock data
    assert len(recommendations) > 0
    assert recommendations[0].recommendation is not None


# def test_get_ai_recommendations_basic_functionality(mock_bedrock_client):
#     """Test that get_ai_recommendations returns a list of AIRecommendation objects."""
#     params = SimulationParameters(attendees=1000, open_gates=2, optimization_goal="Maximum Safety")

#     recommendations = get_ai_recommendations(params)

#     assert isinstance(recommendations, list)
#     assert len(recommendations) > 0
#     assert isinstance(recommendations[0], AIRecommendation)
#     # assert recommendations[0].recommendation == "Test Recommendation"
#     assert recommendations[0].reason == "Test Reason"


def test_get_ai_recommendations_safety_goal_prompt(mock_bedrock_client):
    """Test that the Maximum Safety goal creates the appropriate prompt."""
    params = SimulationParameters(attendees=1000, open_gates=2, optimization_goal="Maximum Safety")

    get_ai_recommendations(params)

    # Check that the correct prompt was sent
    call_args = mock_bedrock_client.invoke_model.call_args[1]["body"]
    assert "MAXIMIZE SAFETY" in call_args
    assert "Attendees: 1000" in call_args
    assert "Number of Open Gates: 2" in call_args
    assert "Optimization Goal: Maximum Safety" in call_args
    assert "Deploy additional security personnel" in call_args
    assert "Open all available gates" in call_args


def test_get_ai_recommendations_balanced_goal_prompt(mock_boto3_client, mocker):
    """Test that a different optimization goal changes the prompt sent to the model."""
    # Arrange
    balanced_params = SimulationParameters(
        attendees=5000, open_gates=2, optimization_goal="Balanced Safety & Cost"
    )
    mock_response_stream = MagicMock()
    mock_response_stream.read.return_value = MOCK_SUCCESS_RESPONSE_BODY
    mock_boto3_client.invoke_model.return_value = {"body": mock_response_stream}

    # Act
    get_ai_recommendations(balanced_params)

    # Assert: Check that the prompt sent to the model contains the correct goal string
    mock_boto3_client.invoke_model.assert_called_once()
    # Get the arguments that the mock was called with
    call_args, call_kwargs = mock_boto3_client.invoke_model.call_args
    request_body = json.loads(call_kwargs["body"])
    prompt = request_body["inputText"]

    assert "Balanced Safety & Cost" in prompt

    # Check that the correct prompt was sent
    # call_args = mock_bedrock_client.invoke_model.call_args[1]["body"]
    # assert "BALANCE SAFETY" in call_args
    # assert "Attendees: 1000" in call_args
    # assert "Number of Open Gates: 2" in call_args
    # assert "Optimization Goal: Balanced Safety & Cost" in call_args
    # assert "Optimize existing resources" in call_args
    # assert "Consider the financial impact" in call_args
    # assert "Redistribute existing staff" in call_args
    # assert "Create temporary queueing systems" in call_args


def test_get_ai_recommendations_with_aws_error(mock_bedrock_client):
    """Test that the function gracefully handles AWS errors."""
    from botocore.exceptions import ClientError

    # Configure the mock to raise a ClientError
    response = {"Error": {"Code": "InvalidRequest", "Message": "Test error message"}}
    mock_bedrock_client.invoke_model.side_effect = ClientError(response, "InvokeModel")

    params = SimulationParameters(attendees=1000, open_gates=2, optimization_goal="Maximum Safety")

    # This should not raise an exception but return mock data instead
    with patch("src.stubs.mock_backend.get_ai_recommendations") as mock_get:
        mock_get.return_value = [AIRecommendation(recommendation="Mock Rec", reason="Mock Reason")]
        recommendations = get_ai_recommendations(params)

        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        assert recommendations[0].recommendation == "Mock Rec"
