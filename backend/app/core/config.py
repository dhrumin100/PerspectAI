import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Google Gemini API - MUST be set in .env file
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    
    if not GOOGLE_API_KEY:
        raise ValueError(
            "GOOGLE_API_KEY not found in environment variables. "
            "Please create a .env file in the backend directory with your API key: "
            "GOOGLE_API_KEY=your_new_api_key_here"
        )
    # Using Gemini 2.5 Pro for reliable grounded search support
    MODEL_NAME = "gemini-2.5-pro"
    SEARCH_MODEL_NAME = "gemini-2.5-pro"
    
    # Pinecone Vector Database (optional - gracefully degrades if not configured)
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", "")
    PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT", "us-east-1")
    PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "perspectai-claims")
    
    # Embedding Model Settings
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # 384 dimensions
    EMBEDDING_DIMENSION = 384
    
    # Vector Search Settings
    VECTOR_SIMILARITY_THRESHOLD = 0.75  # Confidence threshold for cached results (lowered for better cache hits)
    VECTOR_TOP_K = 5  # Number of similar claims to retrieve
    VECTOR_DUPLICATE_THRESHOLD = 0.90  # Above this = duplicate, don't store
