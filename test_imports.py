try:
    from s3_storage import S3Storage
    print("SUCCESS: S3Storage imported")
except Exception as e:
    print(f"ERROR: S3Storage import failed: {e}")

try:
    from bedrock_provider import BedrockProvider
    print("SUCCESS: BedrockProvider imported")
except Exception as e:
    print(f"ERROR: BedrockProvider import failed: {e}")

try:
    provider = BedrockProvider()
    print("SUCCESS: BedrockProvider initialized")
except Exception as e:
    print(f"ERROR: BedrockProvider init failed: {e}")