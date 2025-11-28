"""
Embedding generation utility using sentence-transformers.
Provides local, free embeddings for semantic search.
"""
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Union


class EmbeddingService:
    """
    Service for generating text embeddings using sentence-transformers.
    Uses 'all-MiniLM-L6-v2' model - lightweight, fast, and effective.
    """
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """
        Initialize the embedding model.
        
        Args:
            model_name: HuggingFace model name (default: all-MiniLM-L6-v2)
                       This model produces 384-dimensional embeddings
        """
        self.model = SentenceTransformer(model_name)
        self.dimension = 384  # Dimension for all-MiniLM-L6-v2
        
    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Input text to embed
            
        Returns:
            List of floats representing the embedding vector
        """
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts (batch processing).
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()
    
    def similarity(self, text1: str, text2: str) -> float:
        """
        Calculate cosine similarity between two texts.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score between 0 and 1 (1 = identical)
        """
        emb1 = self.model.encode(text1, convert_to_numpy=True)
        emb2 = self.model.encode(text2, convert_to_numpy=True)
        
        # Cosine similarity
        similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
        return float(similarity)


# Singleton instance for reuse across the application
_embedding_service = None

def get_embedding_service() -> EmbeddingService:
    """
    Get or create singleton embedding service instance.
    This avoids loading the model multiple times.
    """
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service
