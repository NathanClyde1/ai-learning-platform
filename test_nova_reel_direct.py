import boto3
import json
import os
from dotenv import load_dotenv

load_dotenv()

def test_nova_reel_direct():
    try:
        # Try different Nova Reel approaches
        client = boto3.client(
            'bedrock-runtime',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name='us-east-1'
        )
        
        # Test 1: Basic invoke_model
        body = {"text": "Create a video about oranges"}
        
        try:
            response = client.invoke_model(
                modelId="amazon.nova-reel-v1:0",
                body=json.dumps(body)
            )
            print("SUCCESS: Nova Reel v1.0 worked")
            return True
        except Exception as e:
            print(f"Nova Reel v1.0 failed: {e}")
        
        # Test 2: Try v1.1
        try:
            response = client.invoke_model(
                modelId="amazon.nova-reel-v1:1", 
                body=json.dumps(body)
            )
            print("SUCCESS: Nova Reel v1.1 worked")
            return True
        except Exception as e:
            print(f"Nova Reel v1.1 failed: {e}")
            
        return False
        
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    test_nova_reel_direct()