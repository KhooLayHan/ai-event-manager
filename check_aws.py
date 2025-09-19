import boto3
from botocore.exceptions import ClientError, NoCredentialsError


def verify_aws_credentials():
    """
    Verifies that the AWS credentials are set up correctly by making a
    simple, read-only API call to AWS.
    """
    try:
        # Create a client for the IAM service. This is a good choice for a
        # simple check as it exists in all regions and requires authentication.
        iam_client = boto3.client("iam")

        # Make a simple API call that gets information about the current user.
        # This will fail if credentials are not configured correctly.
        response = iam_client.get_user()

        user_arn = response["User"]["Arn"]
        user_name = response["User"]["UserName"]

        print("✅ AWS Credentials are valid and working!")
        print(f"   Authenticated as IAM User: {user_name}")
        print(f"   Full ARN: {user_arn}")
        return True

    except NoCredentialsError:
        print("❌ ERROR: AWS credentials not found.")
        print("   Please run 'aws configure' in your terminal.")
        return False
    except ClientError as e:
        # Handle potential errors like invalid keys
        error_code = e.response.get("Error", {}).get("Code")
        if error_code == "InvalidClientTokenId":
            print("❌ ERROR: Your AWS Access Key ID is invalid.")
        elif error_code == "SignatureDoesNotMatch":
            print("❌ ERROR: Your AWS Secret Access Key is likely incorrect.")
        else:
            print(f"❌ An unexpected AWS client error occurred: {e}")
        return False
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
        return False


if __name__ == "__main__":
    verify_aws_credentials()
