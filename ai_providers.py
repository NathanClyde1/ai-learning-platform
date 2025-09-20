import requests
import os
from dotenv import load_dotenv

load_dotenv()

class AIProvider:
    def __init__(self):
        self.gemini_key = os.getenv('GEMINI_API_KEY')
    
    def get_ai_response(self, topic, level, format_type, context=""):
        """Get response from Google Gemini"""
        if not self.gemini_key:
            return None
            
        prompt = self._build_prompt(topic, level, format_type, context)
        
        try:
            response = self._get_gemini_response(prompt)
            if response:
                cleaned = self._clean_response(response)
                return self._format_markdown(cleaned)
            return None
        except Exception as e:
            print(f"Gemini failed: {e}")
            return None
    
    def _clean_response(self, text):
        """Clean response and ensure natural endings"""
        # Remove unwanted AI endings
        unwanted_sections = [
            "Actionable Information:",
            "Key Takeaways:",
            "In summary:",
            "To summarize:"
        ]
        
        for section in unwanted_sections:
            if section in text:
                text = text.split(section)[0]
        
        # Find complete sentences only
        sentences = text.split('.')
        complete_sentences = []
        
        for i, sentence in enumerate(sentences):
            sentence = sentence.strip()
            
            # Skip very short fragments
            if len(sentence) < 15:
                continue
            
            # Add sentence if it's complete or if it's the last one and looks complete
            if i < len(sentences) - 1:  # Not the last sentence
                complete_sentences.append(sentence)
            else:  # Last sentence - check if it looks complete
                if sentence and (sentence.endswith(('!', '?')) or len(sentence) > 30):
                    complete_sentences.append(sentence)
        
        # Join sentences naturally
        result = '. '.join(complete_sentences)
        if result and not result.endswith(('.', '!', '?')):
            result += '.'
            
        return result if result else text
    
    def _format_markdown(self, text):
        """Convert markdown to HTML formatting"""
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
            'ebook': 'in structured format with headings and key points'
        }
        
        context_part = f" Use this context: {context}" if context else ""
        
        return f"""You are an expert educator. {level_instructions[level]} about '{topic}'. 
        {format_instructions[format_type]}.{context_part}
        
        Provide 2-3 key facts with specific examples. Be concise and complete your thoughts. 
        Do not include summary sections or action items."""
    
    def _get_gemini_response(self, prompt):
        """Get response from Google Gemini"""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={self.gemini_key}"
        
        data = {
            'contents': [{
                'parts': [{'text': prompt}]
            }],
            'generationConfig': {
                'maxOutputTokens': 500,
                'temperature': 0.7
            }
        }
        
        response = requests.post(url, json=data)
        
        if response.status_code == 200:
            result = response.json()
            return result['candidates'][0]['content']['parts'][0]['text']
        else:
            raise Exception(f"Gemini API error: {response.status_code}")