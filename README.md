# PerspectAI - Misinformation Detection System

AI-powered fact-checking and misinformation detection system with multi-agent architecture.

## Project Structure

```
perspectai/
├── frontend/                 # React frontend (Vite)
│   ├── src/
│   │   ├── App.jsx          # Main application component
│   │   ├── App.css          # Styling
│   │   └── main.jsx         # Entry point
│   ├── package.json
│   └── vite.config.js
│
├── backend/                  # Python FastAPI backend
│   ├── app/
│   │   ├── agents/          # AI agents
│   │   │   └── rapid_agent.py
│   │   ├── core/            # Core configuration
│   │   │   ├── config.py
│   │   │   └── prompts.py
│   │   ├── models/          # Pydantic schemas
│   │   │   └── schemas.py
│   │   ├── services/        # External services
│   │   │   └── search_service.py
│   │   └── utils/           # Utilities
│   │   └── main.py          # FastAPI application
│   ├── tests/               # Test files
│   ├── requirements.txt
│   └── .env.example
│
└── README.md
```

## Features

### Component 1: Rapid AI Layer (✅ Implemented)
- 🚀 **Fast fact-checking** with Google Gemini
- 🔍 **Intent classification** (Fact-check, Crisis, General, Archive)
- 🌐 **Web search integration** for real-time verification
- 📊 **Structured responses** with confidence scores
- ⚡ **REST API** for easy integration

### Coming Soon
- 🗄️ **Vector Database** integration (Pinecone)
- 🤖 **Multi-agent research pipeline** (9 agents)
- 🚨 **Crisis detection** system
- 📈 **Daily news scraping** and archiving

## Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- Google API Key (for Gemini)

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # or
   source venv/bin/activate  # Linux/Mac
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment:**
   - Copy `.env.example` to `.env`
   - Add your Google API key:
     ```
     GOOGLE_API_KEY=your_api_key_here
     ```

5. **Run the backend:**
   ```bash
   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

   Backend will be available at `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Run the frontend:**
   ```bash
   npm run dev
   ```

   Frontend will be available at `http://localhost:5173`

## API Endpoints

### Health Check
```
GET /
GET /health
```

### Verify Claim
```
POST /api/verify
Content-Type: application/json

{
  "query": "Is this claim true?",
  "use_vector_db": true,
  "require_web_search": false
}
```

**Response:**
```json
{
  "intent": "FACT_CHECK",
  "verdict": "FALSE",
  "confidence": 0.85,
  "summary": "Analysis of the claim...",
  "evidence": {
    "supporting": [],
    "contradicting": ["Source 1"],
    "neutral": []
  },
  "sources": [
    {
      "url": "https://...",
      "title": "...",
      "credibility": "high"
    }
  ],
  "search_used": "web_search",
  "processing_time_ms": 1234
}
```

## Technology Stack

### Frontend
- **React** - UI framework
- **Vite** - Build tool
- **Axios** - HTTP client
- **CSS3** - Modern styling with animations

### Backend
- **FastAPI** - Web framework
- **Google Gemini** - LLM & Search
- **Pydantic** - Data validation
- **Python 3.12** - Programming language

### Coming Soon
- **Pinecone** - Vector database
- **OpenAI** - Embeddings
- **Redis** - Caching

## Development

### Running Both Services

**Option 1: Manual**
```bash
# Terminal 1 - Backend
cd backend
venv\Scripts\activate
python -m uvicorn app.main:app --reload

# Terminal 2 - Frontend
cd frontend
npm run dev
```

**Option 2: Using batch files (Windows)**
```bash
# Run backend
start_backend.bat

# Run frontend (from frontend directory)
npm run dev
```

## Project Status

- [x] Phase 1: Project cleanup
- [x] Component 1: Rapid AI Layer (basic)
- [ ] Vector Database integration
- [ ] Enhanced response parsing
- [ ] Multi-agent research pipeline
- [ ] Crisis detection system
- [ ] Daily scraping automation

## Contributing

This is a hackathon project. Contributions welcome!

## License

MIT License

## Contact

For questions or feedback, create an issue in the repository.

---

**PerspectAI** - Combating Misinformation with AI 🚀
