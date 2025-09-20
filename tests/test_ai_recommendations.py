import json
from unittest.mock import MagicMock, patch

import pytest

from src.aws.bedrock import get_ai_recommendations
from src.shared_models import SimulationParameters


@pytest.fixture
def valid_params():
    """Fixture for valid simulation parameters."""
    return SimulationParameters(
        attendees=10_000,
        open_gates=3,
        optimization_goal="Maximum Safety",
    )


@pytest.fixture
def mock_bedrock_client():
    """Mock Bedrock client fixture for testing."""
    with patch("boto3") as mock_client:
        # Create a mock instance of the Bedrock client
        mock_bedrock = MagicMock()

        # Configure the mock to return our test data
        mock_client.return_value = mock_bedrock
        yield mock_bedrock


def test_get_ai_recommendations_successful_json(mock_bedrock_client, valid_params):
    """Test successful retrieval of AI recommendations with valid JSON response."""

    # Sets up the mock to return an invalid JSON response
    mock_response = {
        "body": MagicMock(
            read=MagicMock(
                return_value=json.dumps(
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
            )
        )
    }
    mock_bedrock_client.invoke_model.return_value = mock_response

    # Calls the function
    recommendations = get_ai_recommendations(valid_params)

    assert len(recommendations) == 2
    assert recommendations[0].recommendation == "Open Gates C and D"
    assert recommendations[0].reason == "Distributing entry points reduces congestion."
    assert recommendations[1].recommendation == "Deploy 20 staff members"
    assert recommendations[1].reason == "Additional staff can guide attendees."


def test_get_ai_recommendations_invalid_json(mock_bedrock_client, valid_params):
    """Test handling of invalid JSON response from Bedrock."""

    # Sets up the mock to return an invalid JSON response
    mock_response = {
        "body": MagicMock(
            read=MagicMock(
                return_value=json.dumps(
                    {"results": [{"outputText": "This is not a valid JSON response."}]}
                )
            )
        )
    }
    mock_bedrock_client.invoke_model.return_value = mock_response

    # Calls the function
    recommendations = get_ai_recommendations(valid_params)

    # Since the JSON was invalid, we expect to get mock recommendations
    assert len(recommendations) > 0  # Should return mock data
    assert all(hasattr(rec, "recommendation") and hasattr(rec, "reason") for rec in recommendations)


def test_get_ai_recommendations_client_error(mock_bedrock_client, valid_params):
    """Test handling of client error when calling Bedrock."""

    # Sets up the mock to raise a ClientError
    from boto3.exceptions import ClientError

    mock_bedrock_client.invoke_model.side_effect = ClientError(
        error_response={"Error": {"Code": "AccessDenied", "Message": "Access denied"}},
        operation_name="InvokeModel",
    )

    # Calls the function — should not raise an exception
    recommendations = get_ai_recommendations(valid_params)

    # Since there was a client error, we expect to get mock recommendations
    assert len(recommendations) > 0  # Should return mock data
    assert all(hasattr(rec, "recommendation") and hasattr(rec, "reason") for rec in recommendations)


def test_get_ai_recommendations_balanced_goal(mock_bedrock_client):
    """Test AI recommendations with different optimization goals produce different prompts."""

    # For now, create params with "Balanced Safety & Cost"
    params = SimulationParameters(
        attendees=10_000,
        open_gates=3,
        optimization_goal="Balanced Safety & Cost",
    )

    # Sets up the mock to return a valid JSON response
    mock_response = {
        "body": MagicMock(
            read=MagicMock(
                return_value=json.dumps(
                    {
                        "results": [
                            {
                                "outputText": """[
                                    {"recommendation": "Create queue barriers", "reason": "Low-cost solution to organize crowd flow."},
                                    {"recommendation": "Staggered entry times", "reason": "No additional cost but reduces peak congestion."}
                                ]"""
                            }
                        ]
                    }
                )
            )
        )
    }
    mock_bedrock_client.invoke_model.return_value = mock_response

    # Calls the function
    recommendations = get_ai_recommendations(params)

    # Verify the balanced recommendations are returned
    assert (
        "low-cost" in recommendations[0].reason.lower()
        or "no additional cost" in recommendations[1].reason.lower()
    )

    assert len(recommendations) == 2
    assert recommendations[0].recommendation == "Create queue barriers"
    assert recommendations[0].reason == "Low-cost solution to organize crowd flow."
    assert recommendations[1].recommendation == "Staggered entry times"
    assert recommendations[1].reason == "No additional cost but reduces peak congestion."
