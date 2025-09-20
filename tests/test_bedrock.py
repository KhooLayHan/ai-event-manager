import sys

from src.aws.bedrock import get_basic_response, verify_bedrock_access


def main():
    """
    Test running the Bedrock API with real credentials and print the results.

    """
    print("Running Bedrock access test...")
    result = verify_bedrock_access()

    print(f"Bedrock access test result: {result['message']}")

    if not result["success"]:
        print("Bedrock access test failed.")
        sys.exit(1)

    # If we have access, testing sending a simple prompt
    print("Testing Titan Text model with a simple prompt...")
    prompt = "Write a haiku about crowd management at events."

    response = get_basic_response("Hello, Bedrock!")

    if response:
        print(f"\nPrompt: {prompt}")
        print(f"Received response from Titan: {response}")
        print("\nSuccessfully communicated with Amazon Bedrock!")
    else:
        print("\nFailed to get a response from Amazon Bedrock Titan Model.")
        sys.exit(1)


if __name__ == "__main__":
    main()
