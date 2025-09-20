import boto3
import os
from dotenv import load_dotenv

load_dotenv()

def create_bucket():
    """Create S3 bucket in correct region"""
    s3_client = boto3.client(
        's3',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name=os.getenv('AWS_REGION')
    )
    
    bucket_name = f"ailearning-{os.getenv('AWS_ACCESS_KEY_ID')[-4:].lower()}"
    region = os.getenv('AWS_REGION')
    
    try:
        if region == 'us-east-1':
            s3_client.create_bucket(Bucket=bucket_name)
        else:
            s3_client.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={'LocationConstraint': region}
            )
        
        print(f"✅ Created bucket: {bucket_name} in {region}")
        print(f"Update your .env file: S3_BUCKET_NAME={bucket_name}")
        return bucket_name
    except Exception as e:
        print(f"❌ Error creating bucket: {e}")
        return None

if __name__ == "__main__":
    create_bucket()