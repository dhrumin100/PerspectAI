# Deep Research System - 9-Agent Fact-Checking Pipeline

A comprehensive multi-agent system for deep fact-checking and misinformation detection, built with CrewAI, LlamaIndex, and LangChain.

## 🎯 Overview

This system implements a 9-agent pipeline for thorough research and fact-checking:

1. **Query Analyzer** - Extracts structured information from user claims
2. **Source Finder** - Discovers relevant sources (News, Academic, Government)
3. **Planning Agent** - Creates research strategy and identifies gaps
4. **Parallel Research** - Deep multi-threaded web research
5. **Data Aggregator** - Builds knowledge graph and timeline
6. **Analysis & Reasoning** - Generates verdict with confidence scores
7. **Report Generator** - Creates comprehensive PDF/Markdown reports
8. **Infographic Generator** - Visual izes results with charts and graphs
9. **Chat Interface** - Interactive Q&A using RAG

## 🚀 Quick Start

### Installation

```bash
# Navigate to deep_research directory
cd d:\perspectai\deep_research

# Create virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
copy .env.example .env
# Edit .env and add your API keys
```

### Running the Streamlit Testing App

```bash
# Activate virtual environment
.\venv\Scripts\activate

# Run Streamlit app
streamlit run streamlit_app/app.py
```

The app will open in your browser at http://localhost:8501

## 📁 Project Structure

```
deep_research/
├── agents/              # Individual agent implementations
├── crew/                # CrewAI orchestration
├── tools/               # Custom tools for agents
├── streamlit_app/       # Testing interface
│   ├── app.py          # Main dashboard
│   └── pages/          # Individual agent test pages
├── config/              # Configuration and prompts
├── models/              # Pydantic schemas
├── tests/               # Unit tests
├── data/                # Cached data
├── reports/             # Generated reports
└── requirements.txt
```

## 🔧 Configuration

Edit `.env` file:

```env
# Required
GOOGLE_API_KEY=your_gemini_api_key

# Optional (for enhanced functionality)
SERPAPI_KEY=your_serpapi_key
NEWS_API_KEY=your_newsapi_key
PINECONE_API_KEY=your_pinecone_key
```

## 🧪 Testing Individual Agents

Each agent can be tested independently using the Streamlit interface:

1. Open the Streamlit app
2. Navigate to the agent's page from the sidebar
3. Enter test input
4. Click "Run Agent"
5. Review output and download results

## 🔗 Integration with Main App

Once all agents are tested, integrate with the FastAPI backend:

```python
# In backend/app/main.py
from deep_research.crew.research_crew import ResearchCrew

@app.post("/api/deep-research")
async def deep_research(request: DeepResearchRequest):
    crew = ResearchCrew()
    result = crew.run(query=request.query)
    return result
```

## 📊 Agent Status

- [x] Agent 1: Query Analyzer - ✅ Implemented
- [ ] Agent 2: Source Finder - 🔨 In Progress
- [ ] Agent 3: Planning Agent - ⏳ Pending
- [ ] Agent 4: Parallel Research - ⏳ Pending
- [ ] Agent 5: Data Aggregator - ⏳ Pending
- [ ] Agent 6: Analysis & Reasoning - ⏳ Pending
- [ ] Agent 7: Report Generator - ⏳ Pending
- [ ] Agent 8: Infographic Generator - ⏳ Pending
- [ ] Agent 9: Chat Interface - ⏳ Pending

## 🤝 Contributing

This is an active development project. Current focus:
- Implementing remaining 8 agents
- Setting up CrewAI orchestration
- Building comprehensive test suite

## 📝 License

Part of the PerspectAI project.
