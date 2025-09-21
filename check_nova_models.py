import boto3
import json
import os
from dotenv import load_dotenv

load_dotenv()

def check_available_models():
    try:
        bedrock_client = boto3.client(
            'bedrock',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name='us-east-1'
        )
        
        # List available foundation models
        response = bedrock_client.list_foundation_models()
        
        nova_models = []
        for model in response['modelSummaries']:
            if 'nova' in model['modelId'].lower():
                nova_models.append({
                    'id': model['modelId'],
                    'name': model['modelName'],
                    'provider': model['providerName']
                })
        
        print("Available Nova models:")
        for model in nova_models:
            print(f"- {model['id']} ({model['name']})")
        
        if not nova_models:
            print("No Nova models found. Nova Reels may not be available yet.")
            
        return nova_models
        
    except Exception as e:
        print(f"Error checking models: {e}")
        return []

if __name__ == "__main__":
    check_available_models()