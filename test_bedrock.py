import boto3
import json
import os
from dotenv import load_dotenv

load_dotenv()

def test_bedrock():
    try:
        # Test Bedrock connection
        bedrock_client = boto3.client(
            'bedrock-runtime',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name='us-east-1'
        )
        
        # Simple test request
        body = {
            "messages": [
                {
                    "role": "user",
                    "content": [{"text": "Say hello"}]
                }
            ],
            "inferenceConfig": {
                "maxTokens": 100,
                "temperature": 0.7
            }
        }
        
        response = bedrock_client.invoke_model(
            modelId="amazon.nova-pro-v1:0",
            body=json.dumps(body)
        )
        
        response_body = json.loads(response['body'].read())
        print("SUCCESS: Bedrock working:", response_body['output']['message']['content'][0]['text'])
        return True
        
    except Exception as e:
        print(f"ERROR: Bedrock error: {e}")
        return False

if __name__ == "__main__":
    test_bedrock()