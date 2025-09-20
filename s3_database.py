import boto3
import json
import os
from dotenv import load_dotenv

load_dotenv()

class S3Database:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
        self.bucket_name = os.getenv('S3_BUCKET_NAME')
        self.topics_file = 'topics.json'
    
    def get_topic(self, topic_name):
        """Get topic from S3"""
        try:
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=self.topics_file
            )
            topics_data = json.loads(response['Body'].read().decode('utf-8'))
            
            # Search for topic
            for topic in topics_data.get('topics', []):
                if topic_name.lower() in topic['name'].lower() or \
                   any(keyword.lower() in topic_name.lower() for keyword in topic.get('keywords', [])):
                    return topic
            return None
        except Exception as e:
            print(f"Error reading from S3: {e}")
            return None
    
    def add_topic(self, name, explanation, level='beginner', keywords=None):
        """Add topic to S3"""
        try:
            # Get existing data
            try:
                response = self.s3_client.get_object(
                    Bucket=self.bucket_name,
                    Key=self.topics_file
                )
                topics_data = json.loads(response['Body'].read().decode('utf-8'))
            except:
                topics_data = {'topics': []}
            
            # Add new topic
            new_topic = {
                'name': name,
                'explanation': explanation,
                'level': level,
                'keywords': keywords or []
            }
            topics_data['topics'].append(new_topic)
            
            # Save back to S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=self.topics_file,
                Body=json.dumps(topics_data, indent=2),
                ContentType='application/json'
            )
            return True
        except Exception as e:
            print(f"Error writing to S3: {e}")
            return False
    
    def initialize_topics(self):
        """Initialize S3 with sample topics"""
        sample_topics = {
            'topics': [
                {
                    'name': 'React',
                    'explanation': 'A JavaScript library for building user interfaces',
                    'level': 'intermediate',
                    'keywords': ['javascript', 'frontend', 'components', 'jsx']
                },
                {
                    'name': 'Python',
                    'explanation': 'A versatile programming language known for its simplicity',
                    'level': 'beginner',
                    'keywords': ['programming', 'scripting', 'data science', 'web']
                },
                {
                    'name': 'Machine Learning',
                    'explanation': 'AI technique that enables computers to learn from data',
                    'level': 'advanced',
                    'keywords': ['ai', 'data', 'algorithms', 'neural networks']
                }
            ]
        }
        
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=self.topics_file,
                Body=json.dumps(sample_topics, indent=2),
                ContentType='application/json'
            )
            print("✅ S3 topics initialized")
            return True
        except Exception as e:
            print(f"❌ Error initializing S3: {e}")
            return False