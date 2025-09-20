import sqlite3
import json
from datetime import datetime

class KnowledgeDB:
    def __init__(self, db_path='knowledge.db'):
        self.db_path = db_path
        self.init_db()
        self.populate_initial_data()
    
    def init_db(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS topics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic_name TEXT UNIQUE NOT NULL,
                category TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS explanations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic_id INTEGER,
                level TEXT NOT NULL,
                content TEXT NOT NULL,
                format_type TEXT DEFAULT 'general',
                FOREIGN KEY (topic_id) REFERENCES topics (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS keywords (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic_id INTEGER,
                keyword TEXT NOT NULL,
                FOREIGN KEY (topic_id) REFERENCES topics (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_topic(self, topic_name, category, explanations, keywords=None):
        """Add a new topic with explanations"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Insert topic
        cursor.execute('INSERT OR IGNORE INTO topics (topic_name, category) VALUES (?, ?)', 
                      (topic_name.lower(), category))
        
        # Get topic ID
        cursor.execute('SELECT id FROM topics WHERE topic_name = ?', (topic_name.lower(),))
        topic_id = cursor.fetchone()[0]
        
        # Insert explanations
        for level, content in explanations.items():
            cursor.execute('INSERT OR REPLACE INTO explanations (topic_id, level, content) VALUES (?, ?, ?)',
                          (topic_id, level, content))
        
        # Insert keywords
        if keywords:
            for keyword in keywords:
                cursor.execute('INSERT OR IGNORE INTO keywords (topic_id, keyword) VALUES (?, ?)',
                              (topic_id, keyword.lower()))
        
        conn.commit()
        conn.close()
    
    def search_topic(self, query):
        """Search for topics by name or keywords"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query_lower = query.lower().strip()
        
        # Direct topic match
        cursor.execute('''
            SELECT t.topic_name, e.level, e.content 
            FROM topics t 
            JOIN explanations e ON t.id = e.topic_id 
            WHERE t.topic_name = ?
        ''', (query_lower,))
        
        results = cursor.fetchall()
        if results:
            conn.close()
            return self._format_results(results)
        
        # Keyword search
        cursor.execute('''
            SELECT DISTINCT t.topic_name, e.level, e.content 
            FROM topics t 
            JOIN keywords k ON t.id = k.topic_id 
            JOIN explanations e ON t.id = e.topic_id 
            WHERE k.keyword LIKE ? OR t.topic_name LIKE ?
        ''', (f'%{query_lower}%', f'%{query_lower}%'))
        
        results = cursor.fetchall()
        conn.close()
        
        return self._format_results(results) if results else None
    
    def _format_results(self, results):
        """Format database results into dictionary"""
        formatted = {}
        for topic_name, level, content in results:
            if topic_name not in formatted:
                formatted[topic_name] = {}
            formatted[topic_name][level] = content
        return formatted
    
    def populate_initial_data(self):
        """Populate database with initial topics"""
        topics_data = {
            'react': {
                'category': 'frontend',
                'explanations': {
                    'beginner': "React is a JavaScript library created by Facebook in 2013. It helps build websites by breaking them into reusable pieces called components. Think of it like LEGO blocks - you create small pieces and combine them to build bigger things.",
                    'intermediate': "React uses a virtual DOM and JSX syntax to efficiently update web interfaces. Components manage state through hooks like useState and useEffect. Popular tools include Create React App, Next.js, and React Router for building single-page applications.",
                    'advanced': "React implements a reconciliation algorithm with fiber architecture for concurrent rendering. Advanced patterns include render props, higher-order components, context API, and custom hooks. Performance optimization uses React.memo, useMemo, and useCallback."
                },
                'keywords': ['jsx', 'components', 'hooks', 'virtual dom', 'frontend', 'ui']
            },
            'javascript': {
                'category': 'programming',
                'explanations': {
                    'beginner': "JavaScript is the programming language that makes websites interactive. Created by Brendan Eich in 1995, it runs in web browsers and lets you create animations, handle clicks, and update content without refreshing the page.",
                    'intermediate': "JavaScript is an interpreted language with dynamic typing, prototypal inheritance, and first-class functions. ES6+ features include arrow functions, destructuring, modules, and async/await. Node.js enables server-side JavaScript development.",
                    'advanced': "JavaScript uses an event loop with call stack, callback queue, and microtask queue. Advanced concepts include closures, hoisting, prototype chain, and execution contexts. V8 engine optimizations include JIT compilation and garbage collection."
                },
                'keywords': ['js', 'programming', 'web', 'browser', 'nodejs', 'es6']
            },
            'python': {
                'category': 'programming',
                'explanations': {
                    'beginner': "Python is a programming language that's easy to read and write. Created by Guido van Rossum in 1991, it uses simple English-like commands to tell computers what to do, making it perfect for beginners to learn coding.",
                    'intermediate': "Python is an interpreted, high-level language with dynamic typing and automatic memory management. Its extensive standard library and frameworks like Django, Flask make it versatile for web development, data science, and automation.",
                    'advanced': "Python implements duck typing with a global interpreter lock (GIL), uses reference counting with cycle detection for garbage collection, and supports metaclasses, decorators, and context managers for advanced programming patterns."
                },
                'keywords': ['programming', 'scripting', 'data science', 'machine learning', 'django', 'flask']
            },
            'machine learning': {
                'category': 'ai',
                'explanations': {
                    'beginner': "Machine learning teaches computers to recognize patterns by showing them lots of examples. Like teaching a child to recognize cats by showing many cat pictures, computers learn to make predictions without being explicitly programmed.",
                    'intermediate': "Machine learning uses statistical algorithms to find patterns in data. Neural networks, decision trees, and regression models train on datasets to make predictions. Popular frameworks include TensorFlow, PyTorch, and scikit-learn.",
                    'advanced': "Machine learning employs gradient descent optimization, backpropagation, and regularization techniques across supervised, unsupervised, and reinforcement learning paradigms. Advanced topics include deep learning architectures, transfer learning, and model interpretability."
                },
                'keywords': ['ai', 'artificial intelligence', 'neural networks', 'deep learning', 'tensorflow', 'pytorch', 'data']
            }
        }
        
        for topic_name, data in topics_data.items():
            self.add_topic(topic_name, data['category'], data['explanations'], data['keywords'])

def get_topic_response(topic, level):
    """Get response from database"""
    db = KnowledgeDB()
    results = db.search_topic(topic)
    
    if results:
        # Get the first matching topic
        topic_data = list(results.values())[0]
        return topic_data.get(level, topic_data.get('beginner', None))
    
    return None