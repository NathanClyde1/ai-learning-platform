import sqlite3
import json
import random
from datetime import datetime, timedelta
from ai_providers import AIProvider

class GameSystem:
    def __init__(self):
        self.db_path = 'game_system.db'
        self.ai_provider = AIProvider()
        self.init_database()
        self.load_challenges()
    
    def init_database(self):
        """Initialize game database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Challenges table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS challenges (
                id INTEGER PRIMARY KEY,
                title TEXT,
                question TEXT,
                correct_answer TEXT,
                options TEXT,
                category TEXT,
                difficulty TEXT,
                points INTEGER,
                time_limit INTEGER
            )
        ''')
        
        # Player progress table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS player_progress (
                user_id TEXT PRIMARY KEY,
                total_points INTEGER DEFAULT 0,
                challenges_completed INTEGER DEFAULT 0,
                current_streak INTEGER DEFAULT 0,
                best_streak INTEGER DEFAULT 0,
                level INTEGER DEFAULT 1
            )
        ''')
        
        # Challenge attempts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS challenge_attempts (
                id INTEGER PRIMARY KEY,
                user_id TEXT,
                challenge_id INTEGER,
                answer TEXT,
                is_correct BOOLEAN,
                points_earned INTEGER,
                time_taken INTEGER,
                completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def load_challenges(self):
        """Load sample challenges into database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if challenges already exist
        cursor.execute('SELECT COUNT(*) FROM challenges')
        if cursor.fetchone()[0] > 0:
            conn.close()
            return
        
        sample_challenges = [
            {
                'title': 'Balance the Equation',
                'question': 'Balance this chemical equation: H₂ + O₂ → ?',
                'correct_answer': 'H₂O',
                'options': json.dumps(['H₂O', 'H₂O₂', 'HO₂', 'H₃O']),
                'category': 'Chemistry',
                'difficulty': 'beginner',
                'points': 10,
                'time_limit': 30
            },
            {
                'title': 'Python Syntax',
                'question': 'What keyword is used to define a function in Python?',
                'correct_answer': 'def',
                'options': json.dumps(['def', 'function', 'func', 'define']),
                'category': 'Programming',
                'difficulty': 'beginner',
                'points': 10,
                'time_limit': 20
            },
            {
                'title': 'Math Challenge',
                'question': 'What is the derivative of x²?',
                'correct_answer': '2x',
                'options': json.dumps(['2x', 'x²', '2', 'x']),
                'category': 'Mathematics',
                'difficulty': 'intermediate',
                'points': 15,
                'time_limit': 25
            },
            {
                'title': 'React Components',
                'question': 'Which hook is used for state management in React?',
                'correct_answer': 'useState',
                'options': json.dumps(['useState', 'useEffect', 'useContext', 'useReducer']),
                'category': 'Programming',
                'difficulty': 'intermediate',
                'points': 15,
                'time_limit': 30
            },
            {
                'title': 'Physics Laws',
                'question': 'What is Newton\'s second law of motion?',
                'correct_answer': 'F = ma',
                'options': json.dumps(['F = ma', 'E = mc²', 'v = u + at', 'P = mv']),
                'category': 'Physics',
                'difficulty': 'beginner',
                'points': 10,
                'time_limit': 35
            }
        ]
        
        for challenge in sample_challenges:
            cursor.execute('''
                INSERT INTO challenges (title, question, correct_answer, options, category, difficulty, points, time_limit)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (challenge['title'], challenge['question'], challenge['correct_answer'], 
                  challenge['options'], challenge['category'], challenge['difficulty'], 
                  challenge['points'], challenge['time_limit']))
        
        conn.commit()
        conn.close()
        print("✅ Sample challenges loaded!")
    
    def get_random_challenge(self, difficulty='beginner', category=None):
        """Get a random challenge for the player"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if category:
            cursor.execute('''
                SELECT id, title, question, correct_answer, options, category, difficulty, points, time_limit
                FROM challenges 
                WHERE difficulty = ? AND category = ?
                ORDER BY RANDOM()
                LIMIT 1
            ''', (difficulty, category))
        else:
            cursor.execute('''
                SELECT id, title, question, correct_answer, options, category, difficulty, points, time_limit
                FROM challenges 
                WHERE difficulty = ?
                ORDER BY RANDOM()
                LIMIT 1
            ''', (difficulty,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'id': result[0],
                'title': result[1],
                'question': result[2],
                'correct_answer': result[3],
                'options': json.loads(result[4]),
                'category': result[5],
                'difficulty': result[6],
                'points': result[7],
                'time_limit': result[8]
            }
        return None
    
    def submit_answer(self, user_id, challenge_id, answer, time_taken):
        """Submit challenge answer and update progress"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get challenge details
        cursor.execute('SELECT correct_answer, points FROM challenges WHERE id = ?', (challenge_id,))
        challenge = cursor.fetchone()
        
        if not challenge:
            conn.close()
            return {'success': False, 'message': 'Challenge not found'}
        
        correct_answer, max_points = challenge
        is_correct = answer.lower().strip() == correct_answer.lower().strip()
        
        # Calculate points (bonus for speed)
        points_earned = 0
        if is_correct:
            speed_bonus = max(0, max_points - (time_taken // 5))  # Lose 1 point per 5 seconds
            points_earned = min(max_points, max(max_points // 2, speed_bonus))
        
        # Record attempt
        cursor.execute('''
            INSERT INTO challenge_attempts (user_id, challenge_id, answer, is_correct, points_earned, time_taken)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, challenge_id, answer, is_correct, points_earned, time_taken))
        
        # Update player progress
        if is_correct:
            cursor.execute('''
                INSERT OR REPLACE INTO player_progress 
                (user_id, total_points, challenges_completed, current_streak, best_streak, level)
                VALUES (?, 
                    COALESCE((SELECT total_points FROM player_progress WHERE user_id = ?), 0) + ?,
                    COALESCE((SELECT challenges_completed FROM player_progress WHERE user_id = ?), 0) + 1,
                    COALESCE((SELECT current_streak FROM player_progress WHERE user_id = ?), 0) + 1,
                    MAX(COALESCE((SELECT best_streak FROM player_progress WHERE user_id = ?), 0), 
                        COALESCE((SELECT current_streak FROM player_progress WHERE user_id = ?), 0) + 1),
                    CASE WHEN COALESCE((SELECT total_points FROM player_progress WHERE user_id = ?), 0) + ? >= 100 
                         THEN 2 ELSE 1 END)
            ''', (user_id, user_id, points_earned, user_id, user_id, user_id, user_id, user_id, points_earned))
        else:
            # Reset streak on wrong answer
            cursor.execute('''
                INSERT OR REPLACE INTO player_progress 
                (user_id, total_points, challenges_completed, current_streak, best_streak, level)
                VALUES (?, 
                    COALESCE((SELECT total_points FROM player_progress WHERE user_id = ?), 0),
                    COALESCE((SELECT challenges_completed FROM player_progress WHERE user_id = ?), 0),
                    0,
                    COALESCE((SELECT best_streak FROM player_progress WHERE user_id = ?), 0),
                    COALESCE((SELECT level FROM player_progress WHERE user_id = ?), 1))
            ''', (user_id, user_id, user_id, user_id, user_id))
        
        conn.commit()
        conn.close()
        
        return {
            'success': True,
            'is_correct': is_correct,
            'points_earned': points_earned,
            'correct_answer': correct_answer,
            'message': 'Correct! Great job!' if is_correct else f'Incorrect. The answer was: {correct_answer}'
        }
    
    def get_player_stats(self, user_id):
        """Get player statistics and progress"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT total_points, challenges_completed, current_streak, best_streak, level
            FROM player_progress WHERE user_id = ?
        ''', (user_id,))
        
        result = cursor.fetchone()
        
        if result:
            stats = {
                'total_points': result[0],
                'challenges_completed': result[1],
                'current_streak': result[2],
                'best_streak': result[3],
                'level': result[4],
                'next_level_points': result[4] * 100,
                'progress_to_next_level': min(100, (result[0] % 100))
            }
        else:
            stats = {
                'total_points': 0,
                'challenges_completed': 0,
                'current_streak': 0,
                'best_streak': 0,
                'level': 1,
                'next_level_points': 100,
                'progress_to_next_level': 0
            }
        
        conn.close()
        return stats
    
    def get_leaderboard(self, limit=10):
        """Get top players leaderboard"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT user_id, total_points, challenges_completed, best_streak, level
            FROM player_progress 
            ORDER BY total_points DESC, best_streak DESC
            LIMIT ?
        ''', (limit,))
        
        results = cursor.fetchall()
        conn.close()
        
        leaderboard = []
        for i, result in enumerate(results):
            leaderboard.append({
                'rank': i + 1,
                'user_id': result[0][:8] + '***',  # Anonymize
                'total_points': result[1],
                'challenges_completed': result[2],
                'best_streak': result[3],
                'level': result[4]
            })
        
        return leaderboard
    
    def get_categories(self):
        """Get all available challenge categories"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT DISTINCT category FROM challenges ORDER BY category')
        categories = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        return categories