import sqlite3

def update_database():
    """Add user_upvotes table to existing database"""
    conn = sqlite3.connect('knowledge_barter.db')
    cursor = conn.cursor()
    
    # Add user_upvotes table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_upvotes (
            id INTEGER PRIMARY KEY,
            user_id TEXT,
            explanation_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, explanation_id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Database updated with user_upvotes table!")

if __name__ == "__main__":
    update_database()