w# AI Learning Platform

A minimal AI-driven platform that simplifies complex topics and supports multiple learning formats using Google Gemini AI.

## Features

- **AI-Driven Explanations**: Uses Google Gemini to explain any topic
- **Multiple Learning Formats**:
  - 💬 Chat: Conversational explanations
  - ✏️ Sketch: Visual descriptions and diagrams
  - 🎥 Video: Script format with timestamps
  - 📚 E-book: Structured chapters with examples
- **Adaptive Learning Levels**: Beginner, Intermediate, Advanced
- **Document Upload**: Upload PDFs, DOCX, or TXT files for context
- **Topic Database**: Curated responses for common topics
- **Modern UI**: Responsive design with animations

## Quick Start

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/ai-learning-platform.git
   cd ai-learning-platform
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and add your Google Gemini API key:
   ```
   GEMINI_API_KEY=your_actual_api_key_here
   ```

4. **Get a free Gemini API key**:
   - Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a free API key
   - Add it to your `.env` file

5. **Run the application**:
   ```bash
   python app.py
   ```

6. **Open your browser**:
   Navigate to `http://localhost:5000`

## Usage

1. Enter any topic you want to learn about
2. Select your learning level (Beginner/Intermediate/Advanced)
3. Choose your preferred format (Chat/Sketch/Video/E-book)
4. Optionally upload documents for additional context
5. Get AI-generated, personalized learning content

## Project Structure

```
ai-learning-platform/
├── app.py                 # Main Flask application
├── ai_providers.py        # Google Gemini AI integration
├── database.py           # SQLite database for topics
├── topics.py             # Static topic definitions
├── add_topics.py         # Script to add new topics
├── templates/
│   └── index.html        # Main web interface
├── static/
│   └── style.css         # Styling and animations
├── uploads/              # Uploaded documents (created automatically)
├── requirements.txt      # Python dependencies
├── .env.example         # Environment variables template
└── README.md            # This file
```

## Adding New Topics

Run the topic addition script:
```bash
python add_topics.py
```

Or add topics programmatically using the database module.

## API Integration

The platform uses Google Gemini AI for unlimited topic coverage. When a topic isn't found in the local database, it automatically queries Gemini for a personalized response.

## Technologies Used

- **Backend**: Flask, SQLite, Google Gemini AI
- **Frontend**: HTML5, CSS3, JavaScript
- **File Processing**: PyPDF2, python-docx
- **Environment**: python-dotenv

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT License - feel free to use this project for learning and development.

## Support

For issues or questions, please open a GitHub issue or contact the maintainers.