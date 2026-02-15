"""
Quick Bedrock connectivity test (us-east-1).
Uses Converse API to match the AI service. Requires valid AWS credentials.
"""
import boto3
import botocore.exceptions

# Load .env from repo root if present (same as AI service)
try:
    from pathlib import Path
    from dotenv import load_dotenv
    root = Path(__file__).resolve().parent.parent
    load_dotenv(root / ".env")
    load_dotenv(root / "services/ai-forecasting-python/.env")
except ImportError:
    pass

def main():
    try:
        bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")
        response = bedrock.converse(
            modelId="us.anthropic.claude-3-5-haiku-20241022-v1:0",
            messages=[{"role": "user", "content": [{"text": "Say hello in one word."}]}],
        )
        text = response["output"]["message"]["content"][0]["text"]
        print("Bedrock OK:", text)
    except botocore.exceptions.ClientError as e:
        code = e.response.get("Error", {}).get("Code", "")
        msg = e.response.get("Error", {}).get("Message", str(e))
        if code == "UnrecognizedClientException" or "security token" in msg.lower():
            print("AWS credentials invalid or expired. Check:")
            print("  - AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY in .env or environment")
            print("  - Or run: aws configure (or aws sso login if using SSO)")
            print("  - Ensure the identity has Bedrock model access in us-east-1")
        else:
            print(f"Bedrock error [{code}]: {msg}")
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    main()

