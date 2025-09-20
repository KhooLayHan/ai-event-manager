import json
import logging
from typing import Dict, List, Optional, Union

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError, NoCredentialsError

from src.shared_models import AIRecommendation, SimulationParameters

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# REAL BACKEND - Placeholder
def get_ai_recommendations(params: SimulationParameters) -> List[AIRecommendation]:
    """
    Get AI recommendations based on the provided simulation parameters.

    Args:
        params (SimulationParameters): The parameters for the AI simulation.

    Returns:
        List[AIRecommendation]: The list of AI recommendation objects.
    """

    # The AI Lead will replace this with their REAL boto3 calls.
    # For now, we return the mock data so the test UI runs.
    from src.stubs.mock_backend import get_ai_recommendations as mock_get

    return mock_get(params)


def get_basic_response(prompt: str) -> Optional[str]:
    """
    Sends a simple prompt to Amazon Bedrock's Titan Text and returns the response.

    Args:
        prompt (str): The input prompt for the model.

    Returns:
        Optional[str]: The response from the model or None if an error occurred.
    """
    try:
        # Initialize the Bedrock client
        bedrock_runtime = boto3.client(
            service="bedrock-runtime",
            region_name="us-east-1",
            config=Config(retries={"max_attempts": 3}),
        )

        # Create the request body for the Titan model
        request_body = {
            "inputText": prompt,
            "textGenerationConfig": {
                "maxTokenCount": 1024,
                "temperature": 0.7,
                "topP": 0.95,
                "stopSequences": ["\n"],
            },
        }

        # Calls the Titan Text model
        logger.info(f"Sending prompt to Amazon Bedrock: {prompt}")
        response = bedrock_runtime.invoke_model(
            modelId="amazon.titan-text-lite-v1",
            body=json.dumps(request_body),
        )

        response_body = json.loads(response["body"].read())
        result_text = response_body.get("result", [{}])[0].get("outputText", "")

        logger.info(f"Received response from Amazon Bedrock: {result_text[:50]}...")
        return result_text

    except NoCredentialsError:
        logger.error("AWS credentials not found. Please configure your AWS credentials.")
        return None

    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code", "Unknown")
        error_message = e.response.get("Error", {}).get("Message", "No message provided")
        logger.error(f"AWS ClientError: {error_code} - {error_message}")
        return None

    except Exception as e:
        logger.error(f"Unexpected error getting basic response from Amazon Bedrock: {str(e)}")
        return None


def verify_bedrock_access() -> Dict[str, Union[bool, str]]:
    """
    Verify access to Amazon Bedrock by invoking a simple model.

    Returns:
        Dict[str, Union[bool, str]]: A dictionary containing the access status and an optional error message.
    """

    try:
        # Try a simple call to list modesl to verify access
        bedrock_client = boto3.client(
            service="bedrock",
            region_name="us-east-1",
            config=Config(retries={"max_attempts": 3}),
        )

        response = bedrock_client.list_foundation_models(byProvider="Amazon", MaxResults=1)

        # If we get here, we have access
        logger.info("✅ Successfully accessed Amazon Bedrock and listed models.")

        model_count = len(response.get("modelSummaries", []))

        return {
            "success": True,
            "message": f"Successfully connected to Amazon Bedrock. Found {model_count} models.",
        }

    except NoCredentialsError:
        logger.error("AWS credentials not found. Please configure your AWS credentials.")
        return {
            "success": False,
            "message": "AWS credentials not found. Please configure your AWS credentials.",
        }

    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code", "Unknown")
        error_message = e.response.get("Error", {}).get("Message", str(e))

        logger.error(f"AWS ClientError: {error_code} - {error_message}")
        return {"success": False, "message": f"AWS ClientError: {error_code} - {error_message}"}

    except Exception as e:
        logger.error(f"Error verifying Amazon Bedrock access: {str(e)}")
        return {"success": False, "message": f"Failed to access Amazon Bedrock: {str(e)}"}

    prompt = "Hello, Bedrock!"
    response = get_basic_response(prompt)

    if response:
        return {"access": True}
    else:
        return {"access": False, "error": "Failed to access Amazon Bedrock"}
