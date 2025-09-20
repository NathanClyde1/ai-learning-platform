import sqlite3
import os

def fix_database():
    """Fix database schema and add sample data"""
    db_path = 'knowledge_barter.db'
    
    # Remove old database if exists
    if os.path.exists(db_path):
        os.remove(db_path)
        print("Removed old database")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create tables with correct schema
    cursor.execute('''
        CREATE TABLE explanations (
            id INTEGER PRIMARY KEY,
            user_id TEXT,
            topic TEXT,
            level TEXT,
            audio_path TEXT,
            transcript TEXT,
            clarity_score INTEGER,
            knowledge_points INTEGER,
            created_at TIMESTAMP,
            upvotes INTEGER DEFAULT 0
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE user_points (
            user_id TEXT PRIMARY KEY,
            total_points INTEGER DEFAULT 0,
            explanations_count INTEGER DEFAULT 0,
            upvotes_given INTEGER DEFAULT 0
        )
    ''')
    
    # Add sample explanations
    sample_explanations = [
        ('user123', 'React', 'beginner', 'React is a JavaScript library for building user interfaces. It uses components to create reusable UI elements.', 8, 8),
        ('user456', 'Python', 'intermediate', 'Python is a versatile programming language known for its clean syntax and extensive libraries for data science, web development, and automation.', 9, 9),
        ('user789', 'Machine Learning', 'advanced', 'Machine learning is a subset of AI that enables computers to learn patterns from data without explicit programming, using algorithms like neural networks.', 7, 7),
        ('user101', 'JavaScript', 'beginner', 'JavaScript is a programming language that runs in web browsers to make websites interactive and dynamic.', 6, 6),
        ('user202', 'CSS', 'intermediate', 'CSS (Cascading Style Sheets) is used to style HTML elements, controlling layout, colors, fonts, and responsive design.', 8, 8)
    ]
    
    for user_id, topic, level, transcript, clarity, points in sample_explanations:
        cursor.execute('''
            INSERT INTO explanations (user_id, topic, level, transcript, clarity_score, knowledge_points, upvotes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, topic, level, transcript, clarity, points, clarity - 5))  # upvotes = clarity - 5
    
    conn.commit()
    conn.close()
    print("✅ Database fixed and sample data added!")

if __name__ == "__main__":
    fix_database()