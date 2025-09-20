import sqlite3
import json
import os
from datetime import datetime
from ai_providers import AIProvider

class KnowledgeBarterSystem:
    def __init__(self):
        self.db_path = 'knowledge_barter.db'
        self.ai_provider = AIProvider()
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # User explanations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS explanations (
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
        
        # User points table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_points (
                user_id TEXT PRIMARY KEY,
                total_points INTEGER DEFAULT 0,
                explanations_count INTEGER DEFAULT 0,
                upvotes_given INTEGER DEFAULT 0
            )
        ''')
        
        # User upvotes tracking table
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
    
    def submit_explanation(self, user_id, topic, level, transcript):
        """Submit user explanation and get AI clarity score"""
        try:
            # Score explanation clarity using AI
            clarity_score = self._score_explanation_clarity(topic, transcript)
            
            # Calculate knowledge points (1-10 based on clarity)
            knowledge_points = max(1, clarity_score)
            
            # Save to database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO explanations 
                (user_id, topic, level, transcript, clarity_score, knowledge_points, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, topic, level, transcript, clarity_score, knowledge_points, datetime.now()))
            
            # Update user points
            cursor.execute('''
                INSERT OR REPLACE INTO user_points 
                (user_id, total_points, explanations_count)
                VALUES (?, 
                    COALESCE((SELECT total_points FROM user_points WHERE user_id = ?), 0) + ?,
                    COALESCE((SELECT explanations_count FROM user_points WHERE user_id = ?), 0) + 1)
            ''', (user_id, user_id, knowledge_points, user_id))
            
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'clarity_score': clarity_score,
                'points_earned': knowledge_points,
                'message': f'Great explanation! You earned {knowledge_points} knowledge points.'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _score_explanation_clarity(self, topic, transcript):
        """Use AI to score explanation clarity (1-10)"""
        prompt = f"""
        Score this student explanation of '{topic}' for clarity and accuracy on a scale of 1-10.
        
        Student explanation: {transcript}
        
        Consider:
        - Accuracy of information
        - Clarity of explanation
        - Use of examples
        - Logical flow
        
        Respond with only a number from 1-10.
        """
        
        try:
            response = self.ai_provider._get_gemini_response(prompt)
            # Extract number from response
            score = int(''.join(filter(str.isdigit, response))[:1] or '5')
            return min(max(score, 1), 10)  # Ensure 1-10 range
        except:
            return 5  # Default score if AI fails
    
    def get_community_explanations(self, topic, limit=5):
        """Get peer explanations for upvoting"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if topic == 'all':
            cursor.execute('''
                SELECT id, user_id, topic, level, transcript, clarity_score, upvotes
                FROM explanations 
                ORDER BY upvotes DESC, clarity_score DESC
                LIMIT ?
            ''', (limit,))
        else:
            cursor.execute('''
                SELECT id, user_id, topic, level, transcript, clarity_score, upvotes
                FROM explanations 
                WHERE topic LIKE ? 
                ORDER BY upvotes DESC, clarity_score DESC
                LIMIT ?
            ''', (f'%{topic}%', limit))
        
        explanations = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': exp[0],
                'user_id': exp[1][:8] + '***',  # Anonymize
                'topic': exp[2],
                'level': exp[3],
                'transcript': exp[4],
                'clarity_score': exp[5],
                'upvotes': exp[6]
            }
            for exp in explanations
        ]
    
    def upvote_explanation(self, user_id, explanation_id):
        """Upvote a peer explanation (only once per user)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Check if user already upvoted this explanation
            cursor.execute('''
                SELECT id FROM user_upvotes 
                WHERE user_id = ? AND explanation_id = ?
            ''', (user_id, explanation_id))
            
            if cursor.fetchone():
                conn.close()
                return {'success': False, 'message': 'You already upvoted this explanation!'}
            
            # Record the upvote
            cursor.execute('''
                INSERT INTO user_upvotes (user_id, explanation_id)
                VALUES (?, ?)
            ''', (user_id, explanation_id))
            
            # Increment upvote count on explanation
            cursor.execute('''
                UPDATE explanations 
                SET upvotes = upvotes + 1 
                WHERE id = ?
            ''', (explanation_id,))
            
            # Update user upvotes given count
            cursor.execute('''
                INSERT OR REPLACE INTO user_points 
                (user_id, total_points, explanations_count, upvotes_given)
                VALUES (?, 
                    COALESCE((SELECT total_points FROM user_points WHERE user_id = ?), 0),
                    COALESCE((SELECT explanations_count FROM user_points WHERE user_id = ?), 0),
                    COALESCE((SELECT upvotes_given FROM user_points WHERE user_id = ?), 0) + 1)
            ''', (user_id, user_id, user_id, user_id))
            
            conn.commit()
            conn.close()
            
            return {'success': True, 'message': 'Upvoted successfully!'}
            
        except sqlite3.IntegrityError:
            conn.close()
            return {'success': False, 'message': 'You already upvoted this explanation!'}
        except Exception as e:
            conn.close()
            return {'success': False, 'message': f'Error: {str(e)}'}
    
    def get_user_stats(self, user_id):
        """Get user knowledge points and stats"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT total_points, explanations_count, upvotes_given
            FROM user_points WHERE user_id = ?
        ''', (user_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'total_points': result[0],
                'explanations_count': result[1],
                'upvotes_given': result[2],
                'can_redeem_mentorship': result[0] >= 50,
                'can_redeem_bonus_ai': result[0] >= 20
            }
        return {'total_points': 0, 'explanations_count': 0, 'upvotes_given': 0}