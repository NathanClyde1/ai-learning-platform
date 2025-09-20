#!/usr/bin/env python3
"""Script to add new topics to the knowledge database"""

from database import KnowledgeDB

def add_new_topics():
    """Add more topics to expand the knowledge base"""
    db = KnowledgeDB()
    
    new_topics = {
        'aws': {
            'category': 'cloud',
            'explanations': {
                'beginner': "Amazon Web Services (AWS) is like renting computer power from Amazon instead of buying your own servers. Launched in 2006, it offers services like storage (S3), computing (EC2), and databases that you pay for as you use.",
                'intermediate': "AWS provides 200+ cloud services including compute (EC2, Lambda), storage (S3, EBS), databases (RDS, DynamoDB), and networking (VPC, CloudFront). Services are deployed across global regions and availability zones for reliability.",
                'advanced': "AWS architecture patterns include microservices with API Gateway, event-driven systems using EventBridge, and serverless computing with Lambda. Advanced services include EKS for Kubernetes, SageMaker for ML, and Well-Architected Framework principles."
            },
            'keywords': ['cloud', 'amazon', 'ec2', 's3', 'lambda', 'serverless', 'infrastructure']
        },
        'docker': {
            'category': 'devops',
            'explanations': {
                'beginner': "Docker is like a shipping container for software. Created by Solomon Hykes in 2013, it packages your application with everything it needs to run, so it works the same way on any computer - your laptop, servers, or the cloud.",
                'intermediate': "Docker uses containerization to isolate applications using Linux namespaces and cgroups. Key concepts include images, containers, Dockerfile for building, Docker Compose for multi-container apps, and registries like Docker Hub for sharing.",
                'advanced': "Docker implements container runtime using containerd and runc. Advanced features include multi-stage builds, BuildKit for improved performance, Docker Swarm for orchestration, and security scanning. Integration with Kubernetes via CRI."
            },
            'keywords': ['containers', 'containerization', 'devops', 'deployment', 'microservices']
        },
        'blockchain': {
            'category': 'technology',
            'explanations': {
                'beginner': "Blockchain is like a digital ledger that everyone can see but no one can cheat. Each new transaction gets added as a 'block' and linked to previous blocks, creating an unchangeable chain of records.",
                'intermediate': "Blockchain creates immutable distributed ledgers through cryptographic hashing and consensus mechanisms. Each block contains transaction data, timestamps, and hash pointers, forming a tamper-evident chain validated by network participants.",
                'advanced': "Blockchain implements cryptographic hash functions, merkle trees, and distributed consensus protocols (PoW, PoS, PBFT) to achieve Byzantine fault tolerance in decentralized systems while maintaining data integrity and preventing double-spending attacks."
            },
            'keywords': ['cryptocurrency', 'bitcoin', 'ethereum', 'distributed ledger', 'consensus', 'crypto']
        }
    }
    
    for topic_name, data in new_topics.items():
        db.add_topic(topic_name, data['category'], data['explanations'], data['keywords'])
        print(f"Added topic: {topic_name}")

if __name__ == "__main__":
    add_new_topics()
    print("Topics added successfully!")