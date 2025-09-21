import json
from unittest.mock import MagicMock, patch

import pytest

from src.aws.bedrock import get_basic_response, verify_bedrock_access


class MockResponse:
    """
    Mock response class for simulating API responses.
    """

    def __init__(self, body_dict):
        self.body_dict = body_dict

    def get(self, key):
        if key == "body":
            return self

    def read(self):
        return json.dumps(self.body_dict)


@pytest.fixture
def mock_bedrock_client():
    """
    Mock Bedrock client fixture for testing.
    """

    with patch("boto3.client") as mock_client:
        # Create a mock instance of the Bedrock client
        mock_bedrock = MagicMock()

        # Configure the invoke_model method to return a successful mock response
        mock_response = MockResponse(
            {"results": [{"outputText": "This is a test response from Titan model"}]}
        )
        mock_bedrock.invoke_model.return_value = {"body": mock_response}  # No exception by default

        # Configure the list_foundation_models method
        mock_bedrock.list_foundation_models.return_value = {
            "modelSummaries": [{"modelId": "amazon.titan-text-lite-v1"}]
        }

        # Configure the client factory to return our mock
        mock_client.return_value = mock_bedrock
        yield mock_bedrock


@patch("boto3.client")
def test_get_basic_response_client_error(mock_client):
    """
    Test `get_basic_response` function with client error handles gracefully.
    """

    # Configure the client to raise a ClientError
    from botocore.exceptions import ClientError

    mock_bedrock = MagicMock()
    mock_bedrock.invoke_model.side_effect = ClientError(
        error_response={"Error": {"Code": "AccessDenied", "Message": "Access denied"}},
        operation_name="InvokeModel",
    )
    mock_client.return_value = mock_bedrock

    # Calls the function and verify it returns None
    response = get_basic_response("Test prompt")
    assert response is None


def test_verify_bedrock_access_success(mock_bedrock_client):
    """
    Test `verify_bedrock_access` function for successful access.
    """

    result = verify_bedrock_access()
    assert result["success"] is True
    assert "Successfully connected to Amazon Bedrock. Found 1 models." in result["message"]
