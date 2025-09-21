# AI Learning Platform - System Architecture

## 🏗️ High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INTERFACE                          │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐│
│  │    Learn    │ │ Teach Back  │ │ Challenges  │ │   Upload    ││
│  │   Content   │ │ Community   │ │    Game     │ │    Files    ││
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘│
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FLASK WEB SERVER                          │
│                        (app.py)                                │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐│
│  │   Routes    │ │ File Upload │ │ API Endpoints│ │ Static Files││
│  │ Management  │ │  Handler    │ │   Handler   │ │   Server    ││
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘│
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    CORE PLATFORM LAYER                         │
│                  (AILearningPlatform)                          │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐│
│  │ AI Provider │ │ S3 Database │ │ Barter Sys  │ │ Game System ││
│  │ Integration │ │ Integration │ │ Integration │ │ Integration ││
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘│
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      SERVICE LAYER                             │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐│
│  │   AWS       │ │   Local     │ │ Knowledge   │ │    Game     ││
│  │  Bedrock    │ │  SQLite     │ │   Barter    │ │   Engine    ││
│  │  + Polly    │ │  Database   │ │   System    │ │             ││
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘│
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                     DATA STORAGE LAYER                         │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐│
│  │    AWS S3   │ │   SQLite    │ │   SQLite    │ │ Local Files ││
│  │  (Topics)   │ │ (Community) │ │  (Games)    │ │ (Uploads)   ││
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

## 🔧 Component Architecture

### 1. **Frontend Layer**
```
┌─────────────────────────────────────────┐
│            HTML5 + CSS3 + JS            │
├─────────────────────────────────────────┤
│ • Responsive Design                     │
│ • Custom Dropdown Components           │
│ • Real-time Game Timer                  │
│ • Audio Player Integration              │
│ • File Upload Interface                 │
│ • Custom Notifications                  │
└─────────────────────────────────────────┘
```

### 2. **Application Layer**
```
┌─────────────────────────────────────────┐
│              Flask Server               │
├─────────────────────────────────────────┤
│ Routes:                                 │
│ • /learn (POST) - AI Content           │
│ • /game/* - Challenge System           │
│ • /community/* - Barter System         │
│ • /uploads/* - File Serving            │
│                                         │
│ Features:                               │
│ • File Processing (PDF, DOCX, TXT)     │
│ • Session Management                    │
│ • Error Handling                        │
│ • Security (File Upload Validation)    │
└─────────────────────────────────────────┘
```

### 3. **Business Logic Layer**
```
┌─────────────────────────────────────────┐
│         AILearningPlatform              │
├─────────────────────────────────────────┤
│ • Content Format Processing             │
│ • Learning Level Adaptation             │
│ • Multi-modal Content Generation        │
│ • File Text Extraction                  │
│ • Smart Fallback System                 │
└─────────────────────────────────────────┘
```

### 4. **Service Integration Layer**

#### **AI Services (AWS)**
```
┌─────────────────────────────────────────┐
│           BedrockProvider               │
├─────────────────────────────────────────┤
│ • AWS Bedrock Nova Pro Integration      │
│ • Text-to-Speech (AWS Polly)           │
│ • Prompt Engineering                    │
│ • Response Formatting                   │
│ • Error Handling & Fallbacks           │
└─────────────────────────────────────────┘
```

#### **Database Services**
```
┌─────────────────────────────────────────┐
│            S3Database                   │
├─────────────────────────────────────────┤
│ • AWS S3 Integration                    │
│ • Topic Storage & Retrieval             │
│ • Caching Layer                         │
└─────────────────────────────────────────┘
```

#### **Community System**
```
┌─────────────────────────────────────────┐
│        KnowledgeBarterSystem            │
├─────────────────────────────────────────┤
│ • User Explanation Submission           │
│ • Reddit-style Upvoting                 │
│ • Duplicate Prevention                   │
│ • User Statistics                       │
│ • Leaderboard Generation                │
└─────────────────────────────────────────┘
```

#### **Gaming System**
```
┌─────────────────────────────────────────┐
│             GameSystem                  │
├─────────────────────────────────────────┤
│ • Challenge Generation                   │
│ • Category-based Filtering              │
│ • Real-time Scoring                     │
│ • Streak Tracking                       │
│ • Progress Management                   │
│ • Global Leaderboards                   │
└─────────────────────────────────────────┘
```

## 📊 Data Flow Architecture

### **Learning Content Flow**
```
User Input → Flask Route → AILearningPlatform → BedrockProvider → AWS Bedrock Nova Pro
     ↓                                                                      ↓
File Upload → Text Extraction → Context Addition → Prompt Engineering → AI Response
     ↓                                                                      ↓
Format Selection → Content Formatting → AWS Polly (Video) → HTML Response → User
```

### **Community Barter Flow**
```
User Explanation → KnowledgeBarterSystem → SQLite Storage → Community Display
        ↓                    ↓                    ↓              ↓
   Upvote Action → Duplicate Check → Points Update → Stats Update → Leaderboard
```

### **Gaming Challenge Flow**
```
Difficulty + Category → GameSystem → Challenge Selection → Timer Start → User Answer
         ↓                 ↓              ↓                ↓            ↓
    Database Query → Random Selection → Frontend Display → Time Tracking → Score Calculation
         ↓                                                                    ↓
    Progress Update → Streak Management → Level Calculation → Leaderboard Update
```

## 🗄️ Database Schema

### **S3 Database (Topics)**
```sql
{
  "topic_id": "string",
  "topic_name": "string", 
  "explanation": "text",
  "category": "string",
  "difficulty": "string",
  "created_at": "timestamp"
}
```

### **Knowledge Barter Database**
```sql
-- Explanations Table
CREATE TABLE explanations (
    id INTEGER PRIMARY KEY,
    user_id TEXT,
    topic TEXT,
    level TEXT,
    transcript TEXT,
    clarity_score INTEGER,
    knowledge_points INTEGER,
    upvotes INTEGER DEFAULT 0,
    created_at TIMESTAMP
);

-- User Points Table
CREATE TABLE user_points (
    user_id TEXT PRIMARY KEY,
    total_points INTEGER DEFAULT 0,
    explanations_count INTEGER DEFAULT 0,
    upvotes_given INTEGER DEFAULT 0
);

-- User Upvotes Tracking
CREATE TABLE user_upvotes (
    id INTEGER PRIMARY KEY,
    user_id TEXT,
    explanation_id INTEGER,
    created_at TIMESTAMP,
    UNIQUE(user_id, explanation_id)
);
```

### **Game System Database**
```sql
-- Challenges Table
CREATE TABLE challenges (
    id INTEGER PRIMARY KEY,
    title TEXT,
    question TEXT,
    correct_answer TEXT,
    options TEXT, -- JSON array
    category TEXT,
    difficulty TEXT,
    points INTEGER,
    time_limit INTEGER
);

-- Player Progress Table
CREATE TABLE player_progress (
    user_id TEXT PRIMARY KEY,
    total_points INTEGER DEFAULT 0,
    challenges_completed INTEGER DEFAULT 0,
    current_streak INTEGER DEFAULT 0,
    best_streak INTEGER DEFAULT 0,
    level INTEGER DEFAULT 1
);

-- Challenge Attempts Table
CREATE TABLE challenge_attempts (
    id INTEGER PRIMARY KEY,
    user_id TEXT,
    challenge_id INTEGER,
    answer TEXT,
    is_correct BOOLEAN,
    points_earned INTEGER,
    time_taken INTEGER,
    completed_at TIMESTAMP
);
```

## 🔐 Security Architecture

### **Input Validation**
- File upload size limits (16MB)
- Secure filename handling
- File type validation (PDF, DOCX, TXT)
- SQL injection prevention

### **AWS Security**
- IAM role-based access
- Environment variable credentials
- Region-specific service access
- API rate limiting

### **Data Protection**
- User ID anonymization
- No sensitive data logging
- Secure file storage
- Session management

## 🚀 Deployment Architecture

### **Development Environment**
```
Local Flask Server (Debug Mode)
├── SQLite Databases (Local Files)
├── File Uploads (Local Directory)
├── AWS Services (Remote)
└── Static Assets (Local Serving)
```

### **Production Recommendations**
```
Load Balancer
├── Flask App Servers (Multiple Instances)
├── AWS RDS (PostgreSQL/MySQL)
├── AWS S3 (File Storage)
├── AWS CloudFront (CDN)
├── AWS ELB (Load Balancing)
└── AWS CloudWatch (Monitoring)
```

## 📈 Scalability Considerations

### **Horizontal Scaling**
- Stateless Flask application design
- Database connection pooling
- Caching layer implementation
- CDN for static assets

### **Performance Optimization**
- AWS Bedrock response caching
- Database query optimization
- File processing optimization
- Lazy loading for large datasets

### **Monitoring & Analytics**
- AWS CloudWatch integration
- User interaction tracking
- Performance metrics
- Error logging and alerting

## 🔄 Integration Points

### **AWS Services**
- **Bedrock**: AI content generation
- **Polly**: Text-to-speech conversion
- **S3**: Topic storage and file hosting
- **IAM**: Access management

### **External Dependencies**
- **PyPDF2**: PDF text extraction
- **python-docx**: Word document processing
- **Flask**: Web framework
- **SQLite**: Local database storage

This architecture provides a scalable, maintainable, and feature-rich AI learning platform with multiple learning modalities and community engagement features.