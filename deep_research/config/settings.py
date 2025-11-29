"""
Deep Research System Configuration
Centralized settings for all agents and tools
"""

import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

class Settings:
    """Main configuration class"""
    
    # Base Paths
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data"
    REPORTS_DIR = BASE_DIR / "reports"
    CACHE_DIR = BASE_DIR / "cache"
    
    # API Keys
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    SERPAPI_KEY = os.getenv("SERPAPI_KEY", "")
    NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", "")
    PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT", "us-east-1")
    
    # LLM Configuration (Gemini API)
    # Using latest Gemini model: gemini-2.0-flash-exp (most advanced as of Nov 2024)
    # Other options: gemini-1.5-pro, gemini-1.5-flash, gemini-exp-1206
    DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gemini-2.0-flash-exp")
    TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", "8192"))  # Increased for better responses
    
    # Agent Settings
    MAX_ITERATIONS = 5
    TIMEOUT_SECONDS = 300
    
    # Search Settings
    MAX_SEARCH_RESULTS = 20
    MIN_RELEVANCE_SCORE = 0.6
    
    # Parallel Processing
    MAX_PARALLEL_AGENTS = 5
    
    # Vector DB
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION = 384
    VECTOR_TOP_K = 10
    
    # Credibility Scoring
    CREDIBILITY_WEIGHTS = {
        "official_source": 1.0,
        "news_media": 0.8,
        "fact_checker": 0.9,
        "academic": 0.85,
        "social_media": 0.3,
        "unknown": 0.5
    }
    
    @classmethod
    def validate(cls):
        """Validate required settings"""
        if not cls.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY is required")
        
        # Create necessary directories
        cls.DATA_DIR.mkdir(exist_ok=True)
        cls.REPORTS_DIR.mkdir(exist_ok=True)
        cls.CACHE_DIR.mkdir(exist_ok=True)
        
        return True

# Validate on import
Settings.validate()
