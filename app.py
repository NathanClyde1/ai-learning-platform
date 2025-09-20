from flask import Flask, render_template, request, jsonify
import boto3
import json
import os
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
from database import get_topic_response
from ai_providers import AIProvider
try:
    import PyPDF2
except ImportError:
    PyPDF2 = None
try:
    import docx
except ImportError:
    docx = None

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# Create uploads directory
os.makedirs('uploads', exist_ok=True)

class AILearningPlatform:
    def __init__(self):
        self.learning_formats = ['chat', 'sketch', 'video', 'ebook']
        self.bedrock_available = False
        self.ai_provider = AIProvider()
        
        # Try to initialize Bedrock client
        try:
            self.bedrock = boto3.client(
                'bedrock-runtime',
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                region_name=os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
            )
            self.bedrock_available = True
            print("Bedrock connected successfully!")
        except Exception as e:
            print(f"Bedrock not available: {e}")
            print("Using fallback AI system...")
            self.bedrock_available = False
        
    def extract_text_from_file(self, filepath):
        """Extract text from uploaded files"""
        try:
            if filepath.endswith('.txt'):
                with open(filepath, 'r', encoding='utf-8') as f:
                    return f.read()[:5000]
            elif filepath.endswith('.pdf') and PyPDF2:
                with open(filepath, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    text = ""
                    for page in reader.pages[:3]:
                        text += page.extract_text()
                    return text[:5000]
            elif filepath.endswith('.docx') and docx:
                doc = docx.Document(filepath)
                text = ""
                for para in doc.paragraphs[:20]:
                    text += para.text + "\n"
                return text[:5000]
            return ""
        except Exception as e:
            print(f"Error extracting text: {e}")
            return ""
    
    def get_bedrock_response(self, topic, complexity_level, format_type, context=""):
        """Get AI response from AWS Bedrock"""
        
        # Always use smart fallback for now since Bedrock credentials need fixing
        return self.get_smart_fallback(topic, complexity_level, format_type)
        
        level_prompts = {
            'beginner': 'Explain in very simple terms that anyone can understand',
            'intermediate': 'Explain with moderate detail and some technical terms',
            'advanced': 'Provide comprehensive explanation with technical depth'
        }
        
        format_prompts = {
            'chat': 'in a conversational, friendly tone with questions and interactive elements',
            'sketch': 'with detailed visual descriptions, ASCII diagrams, and step-by-step visual breakdowns',
            'video': 'as a complete video script with timestamps, scene descriptions, and narration cues',
            'ebook': 'as structured chapters with headings, bullet points, examples, and exercises'
        }
        
        context_prompt = f" Reference this additional context: {context}" if context else ""
        prompt = f"You are an expert educator. {level_prompts[complexity_level]} the topic '{topic}' with specific facts, examples, and details.{context_prompt} {format_prompts[format_type]}. Include real names, dates, companies, or specific examples related to {topic}. Avoid generic explanations - be topic-specific with concrete information."
        
        try:
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1000,
                "messages": [{"role": "user", "content": prompt}]
            }
            
            response = self.bedrock.invoke_model(
                modelId='anthropic.claude-3-haiku-20240307-v1:0',
                body=json.dumps(body)
            )
            
            response_body = json.loads(response['body'].read())
            return response_body['content'][0]['text'].strip()
            
        except Exception as e:
            print(f"Bedrock error: {e}")
            return self.get_smart_fallback(topic, complexity_level, format_type)
    
    def get_smart_fallback(self, topic, complexity_level, format_type):
        """Smart fallback system with good explanations"""
        
        # Check comprehensive topic database first
        specific_response = get_topic_response(topic, complexity_level)
        if specific_response:
            return specific_response
        
        # Try AI providers for any topic
        ai_response = self.ai_provider.get_ai_response(topic, complexity_level, format_type, "")
        if ai_response:
            return ai_response
        
        # Comprehensive topic-specific explanations
        explanations = {
            'cryptocurrency': {
                'beginner': "Cryptocurrency is digital money stored on computers. Like Bitcoin, you can send it directly to others without using banks. It uses special math codes to keep transactions secure and prevent counterfeiting.",
                'intermediate': "Cryptocurrency operates on blockchain networks using cryptographic algorithms. Miners validate transactions through proof-of-work consensus, creating immutable ledgers that eliminate intermediaries while maintaining decentralized control.",
                'advanced': "Cryptocurrency leverages distributed ledger technology with cryptographic hash functions, merkle trees, and consensus mechanisms like PoW/PoS to achieve Byzantine fault tolerance in trustless peer-to-peer value transfer systems."
            },
            'machine learning': {
                'beginner': "Machine learning teaches computers to recognize patterns by showing them lots of examples. Like teaching a child to recognize cats by showing many cat pictures, computers learn to make predictions.",
                'intermediate': "Machine learning uses statistical algorithms to find patterns in data. Neural networks, decision trees, and regression models train on datasets to make predictions without explicit programming for each scenario.",
                'advanced': "Machine learning employs gradient descent optimization, backpropagation, and regularization techniques across supervised, unsupervised, and reinforcement learning paradigms to minimize loss functions and generalize from training data."
            },
            'python': {
                'beginner': "Python is a programming language that's easy to read and write. It uses simple English-like commands to tell computers what to do, making it perfect for beginners to learn coding.",
                'intermediate': "Python is an interpreted, high-level language with dynamic typing and automatic memory management. Its extensive standard library and frameworks like Django make it versatile for web development, data science, and automation.",
                'advanced': "Python implements duck typing with a global interpreter lock (GIL), uses reference counting with cycle detection for garbage collection, and supports metaclasses, decorators, and context managers for advanced programming patterns."
            },
            'quantum computing': {
                'beginner': "Quantum computers use tiny particles that can be in multiple states at once, unlike regular computers that use just 0s and 1s. This lets them solve certain problems much faster.",
                'intermediate': "Quantum computing exploits quantum superposition and entanglement to process information. Qubits can exist in multiple states simultaneously, enabling parallel computation through quantum algorithms like Shor's and Grover's.",
                'advanced': "Quantum computing utilizes quantum mechanical phenomena including superposition, entanglement, and quantum interference. Gate-based quantum circuits manipulate qubit states through unitary operations to achieve quantum speedup for specific computational problems."
            },
            'blockchain': {
                'beginner': "Blockchain is like a digital ledger that everyone can see but no one can cheat. Each new transaction gets added as a 'block' and linked to previous blocks, creating an unchangeable chain.",
                'intermediate': "Blockchain creates immutable distributed ledgers through cryptographic hashing and consensus mechanisms. Each block contains transaction data, timestamps, and hash pointers, forming a tamper-evident chain validated by network participants.",
                'advanced': "Blockchain implements cryptographic hash functions, merkle trees, and distributed consensus protocols (PoW, PoS, PBFT) to achieve Byzantine fault tolerance in decentralized systems while maintaining data integrity and preventing double-spending attacks."
            }
        }
        
        # Check for specific topics with partial matching
        topic_lower = topic.lower()
        for key, levels in explanations.items():
            if key in topic_lower or any(word in topic_lower for word in key.split()):
                return levels.get(complexity_level, levels['beginner'])
        
        # Enhanced dynamic responses based on topic keywords
        tech_keywords = ['ai', 'artificial intelligence', 'neural', 'algorithm', 'data', 'computer', 'software', 'programming']
        science_keywords = ['physics', 'chemistry', 'biology', 'mathematics', 'theory', 'scientific']
        business_keywords = ['marketing', 'finance', 'economics', 'business', 'management', 'strategy']
        
        if any(keyword in topic_lower for keyword in tech_keywords):
            if complexity_level == 'beginner':
                return f"{topic.capitalize()} is a technology concept that helps solve problems using computers and data. It involves step-by-step processes and logical thinking to create solutions."
            elif complexity_level == 'advanced':
                return f"{topic.capitalize()} involves complex computational algorithms, data structures, and systematic methodologies requiring deep technical understanding and implementation expertise."
            else:
                return f"{topic.capitalize()} combines technical principles with practical applications, using structured approaches to process information and solve real-world problems."
        
        elif any(keyword in topic_lower for keyword in science_keywords):
            if complexity_level == 'beginner':
                return f"{topic.capitalize()} is a scientific concept that explains how things work in nature. It helps us understand patterns and make predictions about the world around us."
            elif complexity_level == 'advanced':
                return f"{topic.capitalize()} encompasses rigorous scientific methodologies, mathematical modeling, and empirical research requiring analytical reasoning and theoretical frameworks."
            else:
                return f"{topic.capitalize()} involves scientific principles and experimental methods to understand natural phenomena and their underlying mechanisms."
        
        elif any(keyword in topic_lower for keyword in business_keywords):
            if complexity_level == 'beginner':
                return f"{topic.capitalize()} is about how organizations work and make decisions. It involves understanding people, money, and strategies to achieve goals."
            elif complexity_level == 'advanced':
                return f"{topic.capitalize()} requires strategic analysis, market dynamics understanding, and complex decision-making frameworks within competitive business environments."
            else:
                return f"{topic.capitalize()} involves business principles, market analysis, and organizational strategies to create value and achieve objectives."
        
        # Generic fallback
        if complexity_level == 'beginner':
            return f"{topic.capitalize()} is an important concept with practical applications. It involves understanding key principles and how they work together in real situations."
        elif complexity_level == 'advanced':
            return f"{topic.capitalize()} requires comprehensive analysis, theoretical understanding, and synthesis of complex interconnected concepts and methodologies."
        else:
            return f"{topic.capitalize()} involves multiple principles and concepts that work together, with practical applications and real-world implications."
        
    def simplify_topic(self, topic, complexity_level, format_type, uploaded_files=None):
        """Main function to get AI explanation for any topic"""
        context = ""
        if uploaded_files:
            for filepath in uploaded_files:
                context += self.extract_text_from_file(filepath) + "\n"
        
        ai_content = self.get_bedrock_response(topic, complexity_level, format_type, context)
        
        formatted_content = self.format_content(ai_content, format_type)
        
        return {
            'content': formatted_content,
            'format': format_type,
            'level': complexity_level
        }
    
    def format_content(self, content, format_type):
        """Apply format-specific styling to content"""
        if format_type == 'chat':
            return f"{content}\n\n💬 Ready to dive deeper? What specific aspect interests you most?"
        
        elif format_type == 'sketch':
            return f"{content}\n\n✏️ Visual tip: Try sketching the key components as you read!"
        
        elif format_type == 'video':
            sentences = content.split('. ')
            if len(sentences) >= 3:
                return f"🎥 [00:00] {sentences[0]}.\n\n[00:30] {sentences[1]}.\n\n[01:00] {sentences[2] if len(sentences) > 2 else sentences[-1]}."
            return f"🎥 [00:00] {content}"
        
        elif format_type == 'ebook':
            return f"📚 **Chapter Overview**\n\n{content}\n\n**Quick Reference:**\n• Core concept explained\n• Real-world applications\n• Next steps for learning"
        
        return content

platform = AILearningPlatform()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/learn', methods=['POST'])
def learn():
    try:
        topic = request.form.get('topic')
        level = request.form.get('level', 'beginner')
        format_type = request.form.get('format', 'chat')
        
        if not topic:
            return jsonify({'error': 'Topic is required'}), 400
        
        uploaded_files = []
        if 'documents' in request.files:
            files = request.files.getlist('documents')
            for file in files:
                if file.filename:
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)
                    uploaded_files.append(filepath)
        
        result = platform.simplify_topic(topic, level, format_type, uploaded_files)
        return jsonify(result)
    except Exception as e:
        print(f"Error in learn route: {e}")
        return jsonify({'error': 'Something went wrong processing your request'}), 500

@app.route('/formats')
def get_formats():
    return jsonify(platform.learning_formats)

if __name__ == '__main__':
    app.run(debug=True)