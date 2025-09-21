import boto3
from botocore.exceptions import ClientError, NoCredentialsError

from src.aws.bedrock import verify_bedrock_access  # Correctly import the function


def verify_aws_setup():
    """
    Verifies the complete AWS setup: IAM credentials and Bedrock access.
    """
    print("--- Verifying AWS Setup ---")

    # Step 1: Verify basic IAM credentials
    print("\n[1/2] Checking basic IAM credentials...")
    try:
        iam_client = boto3.client("iam")
        response = iam_client.get_user()
        user_name = response["User"]["UserName"]
        print(f"✅ Basic IAM credentials are valid. Authenticated as: {user_name}")
    except (NoCredentialsError, ClientError) as e:
        print("❌ Basic IAM credential check FAILED.")
        print(f"   Error: {e}")
        print("   Please run 'aws configure' and ensure your keys are correct.")
        return

    # Step 2: Verify specific access to Bedrock
    print("\n[2/2] Checking Amazon Bedrock service access...")
    bedrock_result = verify_bedrock_access()  # Correct function call

    if bedrock_result["success"]:
        print(f"✅ {bedrock_result['message']}")
        print("\n--- ✅ AWS Setup Complete and Verified! ---")
    else:
        print("❌ Bedrock access check FAILED.")
        print(f"   Error: {bedrock_result['message']}")
        print(
            "   Please ensure your IAM user has permissions for Bedrock and you have requested model access in the console."
        )


if __name__ == "__main__":
    verify_aws_setup()
