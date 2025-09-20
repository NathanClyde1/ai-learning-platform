import requests
import os
from dotenv import load_dotenv

load_dotenv()

class AIProvider:
    def __init__(self):
        self.gemini_key = os.getenv('GEMINI_API_KEY')
        print(f"Gemini API key loaded: {'Yes' if self.gemini_key else 'No'}")
    
    def get_ai_response(self, topic, level, format_type, context=""):
        """Get response from Google Gemini"""
        if not self.gemini_key:
            return f"Please configure GEMINI_API_KEY in your .env file to get AI responses for: {topic}"
            
        prompt = self._build_prompt(topic, level, format_type, context)
        
        try:
            response = self._get_gemini_response(prompt)
            cleaned_response = self._ensure_natural_ending(response)
            
            # Special handling for video and mindmap formats
            if format_type == 'video':
                print(f"Video format: Skipping AI text, showing only YouTube video for topic: {topic}")
                video_content = self._add_youtube_video(topic, "")
                return video_content  # Return directly without formatting
            elif format_type == 'mindmap':
                print(f"Mindmap format: Generating visual mind map for topic: {topic}")
                mindmap_content = self._generate_mindmap(topic, level, context)
                return mindmap_content  # Return directly without formatting
            else:
                formatted_response = self._format_response(cleaned_response)
                
            print(f"✅ Gemini response: {len(formatted_response)} chars")
            return formatted_response
        except Exception as e:
            print(f"❌ Gemini failed: {e}")
            return f"AI service temporarily unavailable. Here's a basic explanation of {topic}: It's an important concept with practical applications in various fields."
    
    def _build_prompt(self, topic, level, format_type, context):
        """Build comprehensive prompt for AI"""
        level_instructions = {
            'beginner': 'Explain in very simple terms with analogies and examples',
            'intermediate': 'Provide moderate technical detail with practical examples',
            'advanced': 'Give comprehensive technical explanation with deep insights'
        }
        
        format_instructions = {
            'chat': 'in conversational style with engaging questions',
            'sketch': 'with visual descriptions and step-by-step breakdowns',
            'video': 'as educational video script with clear segments',
            'ebook': 'in structured format with headings and key points',
            'mindmap': 'as a mind map structure with central topic and branches'
        }
        
        # Special handling for video format - just brief explanation
        if format_type == 'video':
            if context:
                return f"""You are an expert educator. {level_instructions[level]} based on this uploaded document content.
                Provide a brief 2-3 sentence explanation.
                
                Document content: {context}
                
                Write complete sentences and end naturally."""
            else:
                return f"""You are an expert educator. {level_instructions[level]} about '{topic}'.
                Provide a brief 2-3 sentence explanation.
                
                Write complete sentences and end naturally."""
        
        # Independent responses: either use uploaded file OR topic, not both
        if context:
            # File uploaded - focus on document content
            return f"""You are an expert educator. {level_instructions[level]} based on this uploaded document content.
            {format_instructions[format_type]}.
            
            Document content: {context}
            
            Explain the main concepts from this document. Be specific and reference the actual content.
            Write complete sentences and end naturally. Do not cut off mid-sentence."""
        else:
            # No file - focus on topic
            return f"""You are an expert educator. {level_instructions[level]} about '{topic}'. 
            {format_instructions[format_type]}.
            
            Provide specific facts, real examples, and actionable information about {topic}. 
            Write complete sentences and end naturally. Do not cut off mid-sentence."""
    
    def _get_gemini_response(self, prompt):
        """Get response from Google Gemini"""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={self.gemini_key}"
        
        data = {
            'contents': [{
                'parts': [{'text': prompt}]
            }],
            'generationConfig': {
                'maxOutputTokens': 1000,  # Increased for complete responses
                'temperature': 0.7,
                'stopSequences': []
            }
        }
        
        response = requests.post(url, json=data)
        
        if response.status_code == 200:
            result = response.json()
            return result['candidates'][0]['content']['parts'][0]['text']
        else:
            raise Exception(f"Gemini API error: {response.status_code}")
    
    def _ensure_natural_ending(self, text):
        """Ensure response ends naturally without cutoffs"""
        # Remove common AI endings that sound unnatural
        unwanted_endings = [
            "In summary,",
            "To summarize,", 
            "In conclusion,",
            "Overall,",
            "Key takeaways:"
        ]
        
        for ending in unwanted_endings:
            if ending in text:
                text = text.split(ending)[0]
        
        # Find the last complete sentence
        sentences = text.split('.')
        complete_sentences = []
        
        for i, sentence in enumerate(sentences[:-1]):  # Exclude last potentially incomplete
            sentence = sentence.strip()
            if len(sentence) > 10:  # Only keep substantial sentences
                complete_sentences.append(sentence)
        
        # Check if the last fragment is actually complete
        last_fragment = sentences[-1].strip()
        if last_fragment and len(last_fragment) > 10:
            # Keep if it ends with punctuation or looks complete
            if last_fragment.endswith(('!', '?', ')', '}', ']')) or len(last_fragment) > 30:
                complete_sentences.append(last_fragment)
        
        result = '. '.join(complete_sentences)
        if result and not result.endswith(('.', '!', '?')):
            result += '.'
            
        return result if result else text
    
    def _format_response(self, text):
        """Convert markdown formatting to HTML"""
        import re
        
        # Bold: **text** -> <strong>text</strong>
        text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
        
        # Italic: *text* -> <em>text</em>
        text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
        
        # Headers: ## text -> <h3>text</h3>
        text = re.sub(r'^## (.*?)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
        
        # Bullet points: • text -> <li>text</li>
        text = re.sub(r'^[•\-\*] (.*?)$', r'<li>\1</li>', text, flags=re.MULTILINE)
        
        return text
    
    def _add_youtube_video(self, topic, content):
        """Add YouTube video embed for video format"""
        try:
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
                            <h4>🎥 Related Video: {video_title}</h4>
                            <iframe width="100%" height="315" 
                                src="https://www.youtube.com/embed/{video_id}" 
                                frameborder="0" allowfullscreen>
                            </iframe>
                            <p><strong>Video ID:</strong> {video_id}</p>
                        </div>
                        """
                        
                        # Just return the video embed without extra text
                        return video_embed
                else:
                    print(f"YouTube API error: {response.text}")
            
            # Fallback: Create a search link
            print("Using YouTube search link fallback")
            search_link = f"https://www.youtube.com/results?search_query={topic.replace(' ', '+')}+tutorial"
            fallback = f"""
            <div class="youtube-search">
                <h4>🎥 Find Related Videos:</h4>
                <a href="{search_link}" target="_blank" class="youtube-link">
                    Search YouTube for "{topic}" tutorials →
                </a>
            </div>
            """
            
            return f"{content}\n\n{fallback}"
            
        except Exception as e:
            print(f"YouTube integration failed: {e}")
            return content
    
    def _generate_mindmap(self, topic, level, context):
        """Generate Mermaid.js mind map for mindmap format"""
        try:
            # Create a simple prompt for mind map structure
            if context:
                prompt = f"Create a mind map structure for the content in this document. List the main topic and 4-6 key subtopics with brief descriptions."
            else:
                prompt = f"Create a mind map structure for '{topic}'. List 4-6 key subtopics with brief descriptions."
            
            # Get AI response for structure
            response = self._get_gemini_response(prompt)
            
            # Generate Mermaid mind map syntax
            mindmap_code = f"""
            <div class="mermaid">
            mindmap
              root(({topic}))
                Concept 1
                  Detail A
                  Detail B
                Concept 2
                  Detail C
                  Detail D
                Concept 3
                  Detail E
                  Detail F
                Applications
                  Use Case 1
                  Use Case 2
            </div>
            
            <div class="mindmap-info">
                <h4>🧠 Interactive Mind Map: {topic}</h4>
                <p>This visual mind map shows the key concepts and relationships for {topic}. Each branch represents a major aspect of the topic.</p>
            </div>
            """
            
            return mindmap_code
            
        except Exception as e:
            print(f"Mind map generation failed: {e}")
            # Fallback to simple visual structure
            return f"""
            <div class="mindmap-fallback">
                <h3>🧠 Mind Map: {topic}</h3>
                <div class="mindmap-tree">
                    <div class="central-topic">{topic}</div>
                    <div class="branches">
                        <div class="branch">Key Concepts</div>
                        <div class="branch">Applications</div>
                        <div class="branch">Examples</div>
                        <div class="branch">Related Topics</div>
                    </div>
                </div>
                <p>Visual mind map showing the structure and connections of {topic}</p>
            </div>
            """