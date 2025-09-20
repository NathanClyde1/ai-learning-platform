from s3_database import S3Database

def main():
    """Initialize S3 bucket with sample topics"""
    s3_db = S3Database()
    
    print("Initializing S3 database with sample topics...")
    success = s3_db.initialize_topics()
    
    if success:
        print("✅ S3 database initialized successfully!")
        print("Your topics are now stored in S3 bucket")
    else:
        print("❌ Failed to initialize S3 database")
        print("Check your AWS credentials and bucket name")

if __name__ == "__main__":
    main()