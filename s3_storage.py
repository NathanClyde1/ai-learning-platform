import boto3
import json
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class S3Storage:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
        self.bucket_name = os.getenv('S3_BUCKET_NAME')
        print(f"S3 Storage initialized with bucket: {self.bucket_name}")
    
    # Community Barter System Storage
    def submit_explanation(self, user_id, topic, level, transcript, clarity_score=None):
        """Submit explanation to S3"""
        explanation_id = f"exp_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{user_id[:8]}"
        
        explanation_data = {
            'id': explanation_id,
            'user_id': user_id,
            'topic': topic,
            'level': level,
            'transcript': transcript,
            'clarity_score': clarity_score or 5,
            'upvotes': 0,
            'created_at': datetime.now().isoformat()
        }
        
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=f"explanations/{explanation_id}.json",
                Body=json.dumps(explanation_data),
                ContentType='application/json'
            )
            
            # Update user stats
            self._update_user_stats(user_id, 'explanations_count', 1)
            
            return {'success': True, 'message': 'Explanation submitted successfully!', 'clarity_score': clarity_score or 5, 'id': explanation_id}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_community_explanations(self, topic):
        """Get community explanations from S3"""
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix='explanations/'
            )
            
            explanations = []
            if 'Contents' in response:
                for obj in response['Contents']:
                    try:
                        content = self.s3_client.get_object(Bucket=self.bucket_name, Key=obj['Key'])
                        data = json.loads(content['Body'].read())
                        if topic.lower() in data['topic'].lower():
                            explanations.append(data)
                    except:
                        continue
            
            return sorted(explanations, key=lambda x: x['upvotes'], reverse=True)
        except Exception as e:
            print(f"Error getting explanations: {e}")
            return []
    
    def upvote_explanation(self, user_id, explanation_id):
        """Upvote explanation in S3"""
        try:
            # Check if already upvoted
            upvote_key = f"upvotes/{user_id}_{explanation_id}.json"
            try:
                self.s3_client.head_object(Bucket=self.bucket_name, Key=upvote_key)
                return {'success': False, 'message': 'You already upvoted this explanation!'}
            except:
                pass  # Not upvoted yet
            
            # Record upvote
            upvote_data = {
                'user_id': user_id,
                'explanation_id': explanation_id,
                'created_at': datetime.now().isoformat()
            }
            
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=upvote_key,
                Body=json.dumps(upvote_data),
                ContentType='application/json'
            )
            
            # Update explanation upvote count
            exp_key = f"explanations/{explanation_id}.json"
            try:
                content = self.s3_client.get_object(Bucket=self.bucket_name, Key=exp_key)
                data = json.loads(content['Body'].read())
                data['upvotes'] += 1
                
                self.s3_client.put_object(
                    Bucket=self.bucket_name,
                    Key=exp_key,
                    Body=json.dumps(data),
                    ContentType='application/json'
                )
            except:
                pass
            
            # Update user stats
            self._update_user_stats(user_id, 'upvotes_given', 1)
            
            return {'success': True, 'message': 'Upvoted successfully!'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_user_stats(self, user_id):
        """Get user statistics from S3"""
        try:
            content = self.s3_client.get_object(
                Bucket=self.bucket_name, 
                Key=f"users/{user_id}_stats.json"
            )
            return json.loads(content['Body'].read())
        except:
            return {
                'total_points': 0,
                'explanations_count': 0,
                'upvotes_given': 0
            }
    
    def _update_user_stats(self, user_id, field, increment):
        """Update user statistics in S3"""
        try:
            stats = self.get_user_stats(user_id)
            stats[field] = stats.get(field, 0) + increment
            stats['total_points'] = stats.get('explanations_count', 0) * 10 + stats.get('upvotes_given', 0) * 2
            
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=f"users/{user_id}_stats.json",
                Body=json.dumps(stats),
                ContentType='application/json'
            )
        except Exception as e:
            print(f"Error updating user stats: {e}")
    
    # Game System Storage
    def get_random_challenge(self, difficulty='primary', category=None):
        """Get random challenge from S3 or generate with AI"""
        try:
            prefix = f"challenges/{difficulty}/"
            if category:
                prefix += f"{category}/"
            
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            
            if 'Contents' in response and response['Contents']:
                import random
                obj = random.choice(response['Contents'])
                content = self.s3_client.get_object(Bucket=self.bucket_name, Key=obj['Key'])
                return json.loads(content['Body'].read())
            
            # If no stored challenges, try AI generation
            print(f"No stored challenges found, trying AI generation for {category} at {difficulty} level")
            from app import platform
            ai_challenge = platform.ai_provider.generate_ai_challenge(difficulty, category)
            
            if ai_challenge:
                import random
                challenge_id = f"ai_{difficulty}_{category}_{random.randint(1000, 9999)}"
                return {
                    'id': challenge_id,
                    'title': f'{category} Challenge',
                    'category': category or 'General',
                    'difficulty': difficulty,
                    'question': ai_challenge['question'],
                    'options': ai_challenge['options'],
                    'correct_answer': ai_challenge['correct_answer'],
                    'points': 10,
                    'time_limit': 30
                }
            
            return self._generate_ai_challenge(difficulty, category)
            
        except Exception as e:
            print(f"Error getting challenge: {e}")
            return self._generate_ai_challenge(difficulty, category or 'General')
    
    def _generate_ai_challenge(self, difficulty, category):
        """Generate challenge using AI as fallback"""
        import random
        challenge_id = f"ai_{difficulty}_{category}_{random.randint(1000, 9999)}"
        
        # Basic fallback challenge structure
        fallback_challenges = {
            'Mathematics': {
                'primary': {
                    'question': 'What is 7 + 5?',
                    'options': ['10', '11', '12', '13'],
                    'correct_answer': '12'
                },
                'secondary': {
                    'question': 'What is the square root of 64?',
                    'options': ['6', '7', '8', '9'],
                    'correct_answer': '8'
                }
            },
            'Science': {
                'primary': {
                    'question': 'What do plants need to make food?',
                    'options': ['Water only', 'Sunlight only', 'Sunlight and water', 'Soil only'],
                    'correct_answer': 'Sunlight and water'
                },
                'secondary': {
                    'question': 'What is the chemical symbol for water?',
                    'options': ['H2O', 'CO2', 'O2', 'NaCl'],
                    'correct_answer': 'H2O'
                }
            }
        }
        
        # Get challenge data or use default
        if category in fallback_challenges and difficulty in fallback_challenges[category]:
            challenge_data = fallback_challenges[category][difficulty]
        else:
            challenge_data = {
                'question': f'What is an important concept in {category}?',
                'options': ['Option A', 'Option B', 'Option C', 'Option D'],
                'correct_answer': 'Option A'
            }
        
        return {
            'id': challenge_id,
            'title': f'{category} Challenge',
            'category': category or 'General',
            'difficulty': difficulty,
            'question': challenge_data['question'],
            'options': challenge_data['options'],
            'correct_answer': challenge_data['correct_answer'],
            'points': 10,
            'time_limit': 30
        }
    
    def submit_challenge_answer(self, user_id, challenge_id, answer, time_taken):
        """Submit challenge answer to S3"""
        try:
            # Get challenge details
            challenge = self._get_challenge_by_id(challenge_id)
            if not challenge:
                return {'success': False, 'message': 'Challenge not found'}
            
            is_correct = answer.lower().strip() == challenge['correct_answer'].lower().strip()
            points_earned = 0
            
            if is_correct:
                max_points = challenge['points']
                speed_bonus = max(0, max_points - (time_taken // 5))
                points_earned = min(max_points, max(max_points // 2, speed_bonus))
            
            # Record attempt
            attempt_id = f"att_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{user_id[:8]}"
            attempt_data = {
                'id': attempt_id,
                'user_id': user_id,
                'challenge_id': challenge_id,
                'answer': answer,
                'is_correct': is_correct,
                'points_earned': points_earned,
                'time_taken': time_taken,
                'completed_at': datetime.now().isoformat()
            }
            
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=f"attempts/{attempt_id}.json",
                Body=json.dumps(attempt_data),
                ContentType='application/json'
            )
            
            # Update player progress
            self._update_player_progress(user_id, is_correct, points_earned)
            
            message = 'Correct! Great job!' if is_correct else f'Incorrect. The answer was: {challenge["correct_answer"]}'
            
            return {
                'success': True,
                'is_correct': is_correct,
                'points_earned': points_earned,
                'correct_answer': challenge['correct_answer'],
                'message': message
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_player_stats(self, user_id):
        """Get player game statistics from S3"""
        try:
            content = self.s3_client.get_object(
                Bucket=self.bucket_name, 
                Key=f"players/{user_id}_progress.json"
            )
            stats = json.loads(content['Body'].read())
            stats['next_level_points'] = stats['level'] * 100
            stats['progress_to_next_level'] = min(100, (stats['total_points'] % 100))
            return stats
        except:
            return {
                'total_points': 0,
                'challenges_completed': 0,
                'current_streak': 0,
                'best_streak': 0,
                'level': 1,
                'next_level_points': 100,
                'progress_to_next_level': 0
            }
    
    def get_leaderboard(self, limit=10):
        """Get game leaderboard from S3"""
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix='players/'
            )
            
            players = []
            if 'Contents' in response:
                for obj in response['Contents']:
                    try:
                        content = self.s3_client.get_object(Bucket=self.bucket_name, Key=obj['Key'])
                        data = json.loads(content['Body'].read())
                        players.append(data)
                    except:
                        continue
            
            # Sort by points and return top players
            players.sort(key=lambda x: x.get('total_points', 0), reverse=True)
            
            leaderboard = []
            for i, player in enumerate(players[:limit]):
                leaderboard.append({
                    'rank': i + 1,
                    'user_id': player['user_id'][:8] + '***',
                    'total_points': player.get('total_points', 0),
                    'challenges_completed': player.get('challenges_completed', 0),
                    'best_streak': player.get('best_streak', 0),
                    'level': player.get('level', 1)
                })
            
            return leaderboard
        except Exception as e:
            print(f"Error getting leaderboard: {e}")
            return []
    
    def get_categories(self):
        """Get challenge categories from S3"""
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix='challenges/',
                Delimiter='/'
            )
            
            categories = set()
            if 'Contents' in response:
                for obj in response['Contents']:
                    parts = obj['Key'].split('/')
                    if len(parts) >= 3:  # challenges/difficulty/category/
                        categories.add(parts[2])
            
            return sorted(list(categories))
        except Exception as e:
            print(f"Error getting categories: {e}")
            return ['Mathematics', 'Science', 'English', 'History', 'Geography', 'Programming']
    
    def _get_challenge_by_id(self, challenge_id):
        """Get challenge by ID from S3 or memory"""
        try:
            # For AI-generated challenges, recreate from ID
            if challenge_id.startswith('ai_'):
                parts = challenge_id.split('_')
                if len(parts) >= 3:
                    difficulty = parts[1]
                    category = parts[2]
                    return self.get_random_challenge(difficulty, category)
            
            # Search through stored challenges
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix='challenges/'
            )
            
            if 'Contents' in response:
                for obj in response['Contents']:
                    try:
                        content = self.s3_client.get_object(Bucket=self.bucket_name, Key=obj['Key'])
                        data = json.loads(content['Body'].read())
                        if data.get('id') == challenge_id:
                            return data
                    except:
                        continue
            return None
        except Exception as e:
            print(f"Error getting challenge by ID: {e}")
            return None
    
    def _update_player_progress(self, user_id, is_correct, points_earned):
        """Update player progress in S3"""
        try:
            progress = self.get_player_stats(user_id)
            progress['user_id'] = user_id
            
            if is_correct:
                progress['total_points'] += points_earned
                progress['challenges_completed'] += 1
                progress['current_streak'] += 1
                progress['best_streak'] = max(progress['best_streak'], progress['current_streak'])
                progress['level'] = max(1, progress['total_points'] // 100 + 1)
            else:
                progress['current_streak'] = 0
            
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=f"players/{user_id}_progress.json",
                Body=json.dumps(progress),
                ContentType='application/json'
            )
        except Exception as e:
            print(f"Error updating player progress: {e}")
    
    # File Storage
    def upload_file(self, file_path, s3_key):
        """Upload file to S3"""
        try:
            self.s3_client.upload_file(file_path, self.bucket_name, s3_key)
            return f"https://{self.bucket_name}.s3.amazonaws.com/{s3_key}"
        except Exception as e:
            print(f"Error uploading file: {e}")
            return None
    
    def get_file_url(self, s3_key):
        """Get file URL from S3"""
        return f"https://{self.bucket_name}.s3.amazonaws.com/{s3_key}"