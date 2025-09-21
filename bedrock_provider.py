import boto3
import json
import os
from dotenv import load_dotenv

load_dotenv()

class BedrockProvider:
    def __init__(self):
        # Force us-east-1 region for Nova Lite
        self.region = 'us-east-1'
        self.bedrock_client = boto3.client(
            'bedrock-runtime',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=self.region
        )
        self.model_id = "amazon.nova-pro-v1:0"
        print(f"Bedrock client initialized with region: {self.region}")
    
    def get_ai_response(self, topic, level, format_type, context=""):
        """Get response from AWS Bedrock Nova Pro"""
        prompt = self._build_prompt(topic, level, format_type, context)
        
        try:
            print(f"Calling Bedrock for {topic} at {level} level")
            response = self._get_bedrock_response(prompt)
            
            if not response or len(response.strip()) < 10:
                print(f"WARNING: Empty or invalid Bedrock response")
                return None
                
            cleaned_response = self._ensure_natural_ending(response)
            
            # Add Nova Reels video for video format
            if format_type == 'video':
                print(f"Generating Nova Reels video for topic: {topic}")
                video_content = self._generate_nova_reels(topic, cleaned_response)
                formatted_response = self._format_response(video_content)
            elif format_type in ['visual', 'sketch']:
                print(f"Generating Nova Canvas image for topic: {topic}")
                image_content = self._generate_nova_canvas(topic, cleaned_response)
                formatted_response = self._format_response(image_content)
            else:
                formatted_response = self._format_response(cleaned_response)
                
            print(f"SUCCESS: Bedrock response: {len(formatted_response)} chars")
            return formatted_response
        except Exception as e:
            print(f"ERROR: Bedrock failed: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _build_prompt(self, topic, level, format_type, context):
        """Build comprehensive prompt for AI"""
        # Map frontend levels to backend levels
        level_mapping = {
            'beginner': 'primary',
            'intermediate': 'secondary', 
            'advanced': 'foundation'
        }
        
        # Use mapped level or default to the original if not found
        mapped_level = level_mapping.get(level, level)
        
        level_instructions = {
            'primary': 'Explain in very simple terms using fun analogies, everyday examples, and basic vocabulary suitable for Primary school students (Year 1-6)',
            'secondary': 'Explain with clear examples and moderate detail using vocabulary and concepts appropriate for Secondary school students (Form 1-5)',
            'foundation': 'Provide detailed explanations with scientific terms and real-world applications suitable for Foundation/Pre-University students',
            'degree': 'Give comprehensive technical explanations with advanced concepts, research findings, and professional terminology for Degree-level understanding',
            'beginner': 'Explain in very simple terms with analogies and examples',
            'intermediate': 'Provide moderate technical detail with practical examples',
            'advanced': 'Give comprehensive technical explanation with deep insights'
        }
        
        format_instructions = {
            'chat': 'in conversational style with engaging questions',
            'sketch': 'as a brief image description in 1-2 sentences',
            'visual': 'as a brief image description in 1-2 sentences',
            'video': 'as educational video script with clear segments',
            'ebook': 'in structured format with headings and key points',
            'mindmap': 'as a mind map structure with central topic and branches'
        }
        
        if context:
            if topic == 'Document Summary':
                return f"""You are an expert document summarizer. Create a comprehensive summary of this document at {level} level.
                {format_instructions[format_type]}.
                
                Document content: {context}
                
                Summarize the key points, main ideas, and important details from this document. Be thorough and well-organized.
                Write complete sentences and end naturally."""
            else:
                return f"""You are an expert educator. {level_instructions[mapped_level]} based on this uploaded document content.
                {format_instructions[format_type]}.
                
                Document content: {context}
                
                Explain the main concepts from this document. Be specific and reference the actual content.
                Write complete sentences and end naturally."""
        else:
            return f"""You are an expert educator. {level_instructions[mapped_level]} about '{topic}'. 
            {format_instructions[format_type]}.
            
            Provide specific facts, real examples, and actionable information about {topic}. 
            Write complete sentences and end naturally."""
    
    def _get_bedrock_response(self, prompt):
        """Get response from AWS Bedrock Nova Pro"""
        body = {
            "messages": [
                {
                    "role": "user",
                    "content": [{"text": prompt}]
                }
            ],
            "inferenceConfig": {
                "maxTokens": 1000,
                "temperature": 0.7
            }
        }
        
        response = self.bedrock_client.invoke_model(
            modelId=self.model_id,
            body=json.dumps(body)
        )
        
        response_body = json.loads(response['body'].read())
        return response_body['output']['message']['content'][0]['text']
    
    def _ensure_natural_ending(self, text):
        """Ensure response ends naturally without cutoffs"""
        sentences = text.split('.')
        complete_sentences = []
        
        for i, sentence in enumerate(sentences[:-1]):
            sentence = sentence.strip()
            if len(sentence) > 10:
                complete_sentences.append(sentence)
        
        last_fragment = sentences[-1].strip()
        if last_fragment and len(last_fragment) > 10:
            if last_fragment.endswith(('!', '?', ')', '}', ']')) or len(last_fragment) > 30:
                complete_sentences.append(last_fragment)
        
        result = '. '.join(complete_sentences)
        if result and not result.endswith(('.', '!', '?')):
            result += '.'
            
        return result if result else text
    
    def _format_response(self, text):
        """Convert markdown formatting to HTML"""
        import re
        
        # Convert markdown to HTML - order matters (longest patterns first)
        text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
        text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
        text = re.sub(r'^#### (.*?)$', r'<h4>\1</h4>', text, flags=re.MULTILINE)
        text = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
        text = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', text, flags=re.MULTILINE)
        text = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', text, flags=re.MULTILINE)
        
        # Clean up any remaining markdown symbols
        text = re.sub(r'^#{1,6}\s*', '', text, flags=re.MULTILINE)
        text = re.sub(r'\*{1,2}', '', text)
        
        # Convert bullet points to proper lists
        lines = text.split('\n')
        in_list = False
        formatted_lines = []
        
        for line in lines:
            if re.match(r'^[•\-\*] ', line):
                if not in_list:
                    formatted_lines.append('<ul>')
                    in_list = True
                formatted_lines.append(f'<li>{re.sub(r"^[•\-\*] ", "", line)}</li>')
            else:
                if in_list:
                    formatted_lines.append('</ul>')
                    in_list = False
                formatted_lines.append(line)
        
        if in_list:
            formatted_lines.append('</ul>')
        
        return '\n'.join(formatted_lines)
    
    def grade_explanation(self, topic, level, explanation):
        """Grade student explanation using AI"""
        prompt = f"""You are an expert educator grading student explanations. 
        
        Topic: {topic}
        Education Level: {level}
        Student Explanation: {explanation}
        
        Grade this explanation on a scale of 1-10 based on:
        - Accuracy of information (40%)
        - Clarity and organization (30%) 
        - Appropriate complexity for {level} level (20%)
        - Use of examples or analogies (10%)
        
        Respond with ONLY a single number from 1-10. No other text."""
        
        try:
            response = self._get_bedrock_response(prompt)
            print(f"AI Grading Response: {response}")
            
            # Extract number from response
            import re
            score_match = re.search(r'\b([1-9]|10)\b', response)
            if score_match:
                score = int(score_match.group(1))
                print(f"Extracted Score: {score}")
                return score
            
            print("No score found in response, using default")
            return 5  # Default score if parsing fails
        except Exception as e:
            print(f"AI Grading Error: {e}")
            return 5  # Default score if API fails
    
    def _generate_nova_reels(self, topic, content):
        """Generate video using AWS Nova Reels"""
        try:
            # Initialize Nova Reel client - try bedrock-agent-runtime
            try:
                nova_client = boto3.client(
                    'bedrock-agent-runtime',
                    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                    region_name=self.region
                )
            except:
                nova_client = boto3.client(
                    'bedrock-runtime',
                    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                    region_name=self.region
                )
            
            # Nova Reel video generation request - simplified
            body = {
                "text": f"Create a short educational video about {topic} for beginners"
            }
            
            print(f"Generating Nova Reels video for: {topic}")
            
            # Try Nova Reel async job submission
            try:
                response = nova_client.invoke_model(
                    modelId="amazon.nova-reel-v1:1",
                    body=json.dumps(body)
                )
                response_body = json.loads(response['body'].read())
            except Exception as reel_error:
                print(f"Nova Reel v1.1 failed: {reel_error}")
                # Try v1.0
                response = nova_client.invoke_model(
                    modelId="amazon.nova-reel-v1:0",
                    body=json.dumps(body)
                )
                response_body = json.loads(response['body'].read())
            
            # Nova Reel returns video data or job ID
            if 'video' in response_body:
                video_data = response_body['video']
                video_url = video_data.get('s3Uri', '')
                
                # Create video player interface
                video_embed = f"""
                <div class="nova-reels-video">
                    <h4>AI-Generated Video: {topic}</h4>
                    <div class="video-container">
                        <video width="640" height="360" controls>
                            <source src="{video_url}" type="video/mp4">
                            Your browser does not support the video tag.
                        </video>
                    </div>
                    <div class="video-info">
                        <p><strong>Topic:</strong> {topic}</p>
                        <p><strong>Generated by:</strong> AWS Nova Reel</p>
                    </div>
                </div>
                """
            else:
                # Fallback if video generation is async
                video_embed = f"""
                <div class="nova-reels-video">
                    <h4>AI Video Generation: {topic}</h4>
                    <div class="video-container">
                        <div class="video-placeholder">
                            <p>Video generation in progress...</p>
                            <p><strong>Topic:</strong> {topic}</p>
                        </div>
                    </div>
                    <p><small>Powered by AWS Nova Reel</small></p>
                </div>
                """
            
            return video_embed
            
        except Exception as e:
            print(f"Nova Reels generation failed: {e}")
            # Fallback to YouTube video since Nova Reel isn't working
            return self._add_youtube_video(topic, content)
    
    def _add_youtube_video(self, topic, content):
        """Fallback: Add YouTube video embed for video format"""
        try:
            import requests
            search_query = f"{topic} tutorial explanation educational"
            youtube_api_key = os.getenv('YOUTUBE_API_KEY')
            print(f"YouTube API key found: {'Yes' if youtube_api_key else 'No'}")
            
            if youtube_api_key:
                print(f"Searching YouTube for: {search_query}")
                search_url = f"https://www.googleapis.com/youtube/v3/search"
                params = {
                    'part': 'snippet',
                    'q': search_query,
                    'type': 'video',
                    'maxResults': 1,
                    'order': 'relevance',
                    'key': youtube_api_key
                }
                
                response = requests.get(search_url, params=params)
                print(f"YouTube API response: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    if data['items']:
                        video = data['items'][0]
                        video_id = video['id']['videoId']
                        video_title = video['snippet']['title']
                        print(f"Found video: {video_title}")
                        
                        video_embed = f"""
                        <div class="youtube-video">
                            <h4>Related Video: {video_title}</h4>
                            <iframe width="560" height="315" 
                                src="https://www.youtube.com/embed/{video_id}" 
                                frameborder="0" allowfullscreen>
                            </iframe>
                        </div>
                        """
                        
                        return f"{content}\n\n{video_embed}"
                else:
                    print(f"YouTube API error: {response.text}")
            
            # Fallback: Create a search link
            print("Using YouTube search link fallback")
            search_link = f"https://www.youtube.com/results?search_query={topic.replace(' ', '+')}+tutorial"
            fallback = f"""
            <div class="youtube-search">
                <h4>Find Related Videos:</h4>
                <a href="{search_link}" target="_blank" class="youtube-link">
                    Search YouTube for "{topic}" tutorials
                </a>
            </div>
            """
            
            return f"{content}\n\n{fallback}"
            
        except Exception as e:
            print(f"YouTube integration failed: {e}")
            return content
    
    def _generate_nova_canvas(self, topic, content):
        """Generate image using AWS Nova Canvas"""
        try:
            # Nova Canvas image generation request
            body = {
                "taskType": "TEXT_IMAGE",
                "textToImageParams": {
                    "text": f"Educational diagram about {topic}. Clear, simple illustration showing key concepts."
                }
            }
            
            print(f"Generating Nova Canvas image for: {topic}")
            
            # Call Nova Canvas for image generation
            response = self.bedrock_client.invoke_model(
                modelId="amazon.nova-canvas-v1:0",
                body=json.dumps(body),
                contentType="application/json",
                accept="application/json"
            )
            
            response_body = json.loads(response['body'].read())
            
            # Nova Canvas returns image data
            if 'images' in response_body:
                image_data = response_body['images'][0]
                
                # Save image to uploads folder
                import base64
                image_filename = f"canvas_{topic.replace(' ', '_')[:20]}.png"
                image_path = os.path.join('uploads', image_filename)
                
                with open(image_path, 'wb') as img_file:
                    img_file.write(base64.b64decode(image_data))
                
                # Create image display with brief description
                image_embed = f"""
                <div class="nova-canvas-image">
                    <div class="image-container">
                        <img src="/uploads/{image_filename}" alt="{topic} visual" style="max-width: 100%; height: auto;">
                    </div>
                    <p class="image-description">{content}</p>
                </div>
                """
                
                return image_embed
            else:
                # Fallback if image generation fails
                return f"""
                <div class="nova-canvas-placeholder">
                    <div class="image-placeholder">
                        <p>Visual generation in progress...</p>
                    </div>
                </div>
                """
                
        except Exception as e:
            print(f"Nova Canvas generation failed: {e}")
            # Return content with placeholder
            return f"""
            <div class="nova-canvas-error">
                <div class="image-placeholder">
                    <p>Visual temporarily unavailable</p>
                </div>
            </div>
            """
    
    def _add_polly_audio(self, topic, content):
        """Add AWS Polly text-to-speech for audio format"""
        try:
            # Initialize Polly client
            polly_client = boto3.client(
                'polly',
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                region_name=self.region
            )
            
            # Clean text for speech synthesis
            speech_text = content.replace('<strong>', '').replace('</strong>', '')
            speech_text = speech_text.replace('<em>', '').replace('</em>', '')
            speech_text = speech_text.replace('<h3>', '').replace('</h3>', '')
            speech_text = speech_text.replace('<li>', '').replace('</li>', '')
            
            # Limit text length for Polly (max 3000 chars)
            if len(speech_text) > 2500:
                speech_text = speech_text[:2500] + "..."
            
            print(f"Generating speech for {len(speech_text)} characters")
            
            # Generate speech with Polly
            response = polly_client.synthesize_speech(
                Text=speech_text,
                OutputFormat='mp3',
                VoiceId='Joanna'  # Female US English voice
            )
            
            # Save audio file
            audio_filename = f"audio_{topic.replace(' ', '_')[:20]}.mp3"
            audio_path = os.path.join('uploads', audio_filename)
            
            with open(audio_path, 'wb') as audio_file:
                audio_file.write(response['AudioStream'].read())
            
            print(f"Audio saved: {audio_path}")
            
            # Create video-style content with audio player
            video_embed = f"""
            <div class="aws-video-content">
                <h4>🎥 AI-Generated Video Content: {topic}</h4>
                <div class="video-script">
                    <h5>Script:</h5>
                    <p>{content}</p>
                </div>
                <div class="audio-player">
                    <h5>🔊 Listen to AI Narration:</h5>
                    <audio controls style="width: 100%; margin: 10px 0;">
                        <source src="/uploads/{audio_filename}" type="audio/mpeg">
                        Your browser does not support the audio element.
                    </audio>
                    <p><small>Narrated by AWS Polly (Joanna - Neural Voice)</small></p>
                </div>
            </div>
            """
            
            return video_embed
            
        except Exception as e:
            print(f"AWS Polly failed: {e}")
            # Fallback to text-only video format
            fallback = f"""
            <div class="video-fallback">
                <h4>🎥 Video Script: {topic}</h4>
                <div class="script-content">
                    <p>{content}</p>
                </div>
                <p><small>Audio generation temporarily unavailable</small></p>
            </div>
            """
            return fallback
    
    def generate_flashcards(self, topic, level):
        """Generate flashcards using AI"""
        prompt = f"""Generate 5 flashcards for the topic '{topic}' at {level} education level.
        
        Format as JSON array with this exact structure:
        [
            {{"question": "Question text here?", "answer": "Answer text here"}},
            {{"question": "Question text here?", "answer": "Answer text here"}}
        ]
        
        Make questions appropriate for {level} level students.
        Keep questions clear and answers concise but complete.
        Focus on key concepts, definitions, and important facts about {topic}.
        
        Return ONLY the JSON array, no other text."""
        
        try:
            response = self._get_bedrock_response(prompt)
            print(f"Flashcard Response: {response}")
            
            # Extract JSON from response
            import json
            import re
            
            # Find JSON array in response
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                flashcards = json.loads(json_str)
                
                # Validate structure
                if isinstance(flashcards, list) and len(flashcards) > 0:
                    for card in flashcards:
                        if 'question' in card and 'answer' in card:
                            continue
                        else:
                            raise ValueError("Invalid flashcard structure")
                    
                    print(f"Generated {len(flashcards)} flashcards")
                    return flashcards
            
            # Fallback flashcards if parsing fails
            return self._generate_fallback_flashcards(topic, level)
            
        except Exception as e:
            print(f"Flashcard generation error: {e}")
            return self._generate_fallback_flashcards(topic, level)
    
    def _generate_fallback_flashcards(self, topic, level):
        """Generate basic fallback flashcards"""
        return [
            {"question": f"What is {topic}?", "answer": f"{topic} is an important concept in its field of study."},
            {"question": f"Why is {topic} important?", "answer": f"{topic} has practical applications and real-world significance."},
            {"question": f"How does {topic} work?", "answer": f"{topic} involves specific processes and mechanisms."},
            {"question": f"Where is {topic} used?", "answer": f"{topic} is applied in various contexts and situations."},
            {"question": f"What are key features of {topic}?", "answer": f"{topic} has distinctive characteristics and properties."}
        ]
    
    def generate_ai_challenge(self, difficulty, category):
        """Generate challenge question using AI"""
        prompt = f"""Generate a {difficulty} level challenge question for {category} subject.
        
        Format as JSON with this exact structure:
        {{
            "question": "Question text here?",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "correct_answer": "Option A"
        }}
        
        Make the question appropriate for Malaysian {difficulty} education level.
        Ensure one option is clearly correct and others are plausible but wrong.
        Focus on key concepts students should know at this level.
        
        Return ONLY the JSON object, no other text."""
        
        try:
            response = self._get_bedrock_response(prompt)
            print(f"AI Challenge Response: {response}")
            
            # Extract JSON from response
            import json
            import re
            
            # Find JSON object in response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                challenge_data = json.loads(json_str)
                
                # Validate structure
                if all(key in challenge_data for key in ['question', 'options', 'correct_answer']):
                    print(f"Generated AI challenge for {category}")
                    return challenge_data
            
            return None
            
        except Exception as e:
            print(f"AI Challenge generation error: {e}")
            return None
    
    def analyze_blurting(self, topic, level, blurt_text, time_spent):
        """Analyze student's blurting session using AI"""
        prompt = f"""You are an expert educator analyzing a student's "blurting" session (active recall practice).
        
        Topic: {topic}
        Education Level: {level}
        Time Spent: {time_spent} seconds
        Student's Blurting Text: {blurt_text}
        
        Analyze what the student wrote and provide:
        1. What they got RIGHT (key concepts they remembered)
        2. What they MISSED (important concepts not mentioned)
        3. KNOWLEDGE GAPS (areas to study more)
        4. SUGGESTIONS for improvement
        
        Format your response with clear headings and be encouraging but honest about gaps.
        Keep it appropriate for {level} education level.
        
        Focus on helping them identify what to study next."""
        
        try:
            response = self._get_bedrock_response(prompt)
            print(f"Blurting Analysis Response: {len(response)} chars")
            
            # Format the response
            formatted_response = self._format_response(response)
            return formatted_response
            
        except Exception as e:
            print(f"Blurting analysis error: {e}")
            return self._generate_fallback_analysis(topic, level, blurt_text)
    
    def _generate_fallback_analysis(self, topic, level, blurt_text):
        """Generate basic fallback analysis"""
        word_count = len(blurt_text.split())
        
        return f"""
        <h5>✅ What You Did Well:</h5>
        <p>You wrote {word_count} words about {topic}, showing you have some knowledge of the topic.</p>
        
        <h5>🎯 Areas to Explore Further:</h5>
        <p>Consider researching more specific details and examples related to {topic} at the {level} level.</p>
        
        <h5>📚 Study Suggestions:</h5>
        <ul>
            <li>Review key definitions and concepts</li>
            <li>Look for real-world applications</li>
            <li>Practice explaining {topic} to someone else</li>
            <li>Try this blurting exercise again in a few days</li>
        </ul>
        
        <h5>💡 Next Steps:</h5>
        <p>Great job using active recall! This technique helps identify knowledge gaps effectively.</p>
        """