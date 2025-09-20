import json
import logging
import os
from typing import Dict, List, Optional, Union

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError, NoCredentialsError

from src.shared_models import AIRecommendation, SimulationParameters

# Configure logging for the module
logger = logging.getLogger(__name__)

AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")

# Best Practice: Create clients once at the module level.
# Boto3 will automatically use the region and credentials from the user's environment.
# This removes the need for hardcoded regions.
try:
    bedrock_client = boto3.client(
        service_name="bedrock", region_name=AWS_REGION, config=Config(retries={"max_attempts": 3})
    )
    bedrock_runtime_client = boto3.client(
        service_name="bedrock-runtime",
        region_name=AWS_REGION,
        config=Config(retries={"max_attempts": 3}),
    )
except NoCredentialsError:
    logger.error("AWS credentials not found. Please run 'aws configure'.")
    bedrock_client = None
    bedrock_runtime_client = None


# REAL BACKEND - Placeholder (This part is correct)
def get_ai_recommendations(params: SimulationParameters) -> List[AIRecommendation]:
    from src.stubs.mock_backend import get_ai_recommendations as mock_get

    return mock_get(params)


def get_basic_response(prompt: str) -> Optional[str]:
    """Sends a prompt to Amazon Titan Text and returns the response."""
    if not bedrock_runtime_client:
        return None

    try:
        request_body = {
            "inputText": prompt,
            "textGenerationConfig": {"maxTokenCount": 512, "temperature": 0.7, "topP": 0.9},
        }

        logger.info("Sending prompt to Amazon Bedrock Titan model...")
        response = bedrock_runtime_client.invoke_model(
            modelId="amazon.titan-text-lite-v1", body=json.dumps(request_body)
        )

        response_body = json.loads(response["body"].read())
        result_text = response_body["results"][0]["outputText"]

        logger.info("Received response from Amazon Bedrock.")
        return result_text

    except ClientError as e:
        logger.error(f"AWS ClientError calling Bedrock: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error calling Bedrock: {e}")
        return None


def verify_bedrock_access() -> Dict[str, Union[bool, str]]:
    """Verifies access to Amazon Bedrock by listing available foundation models."""
    if not bedrock_client:
        return {
            "success": False,
            "message": "AWS credentials not found. Please configure your AWS credentials.",
        }

    try:
        logger.info("Verifying access to Amazon Bedrock by listing foundation models...")
        # A simple, low-cost API call to check permissions and connectivity.
        response = bedrock_client.list_foundation_models(byProvider="Amazon")

        model_count = len(response.get("modelSummaries", []))
        message = f"Successfully connected to Amazon Bedrock. Found {model_count} Amazon foundation models."
        logger.info(message)

        return {"success": True, "message": message}

    except ClientError as e:
        error_message = (
            f"AWS ClientError: {e.response['Error']['Code']} - {e.response['Error']['Message']}"
        )
        logger.error(error_message)
        return {"success": False, "message": error_message}
    except Exception as e:
        error_message = f"An unexpected error occurred: {e}"
        logger.error(error_message)
        return {"success": False, "message": error_message}
