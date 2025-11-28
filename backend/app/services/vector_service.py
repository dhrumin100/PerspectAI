"""
Vector database service using Pinecone for semantic search over verified claims.
Gracefully handles missing configuration by disabling vector search.
"""
from typing import List, Dict, Optional, Any
import os
from datetime import datetime

try:
    from pinecone import Pinecone, ServerlessSpec
    PINECONE_AVAILABLE = True
except ImportError:
    PINECONE_AVAILABLE = False
    print("WARNING: pinecone not installed. Vector DB features disabled.")

from app.core.config import Config
from app.utils.embeddings import get_embedding_service


class VectorService:
    """
    Service for storing and querying verified claims in vector database.
    Falls back gracefully if Pinecone is not configured.
    """
    
    def __init__(self):
        """Initialize Pinecone connection if configured."""
        self.enabled = False
        self.index = None
        self.embedding_service = get_embedding_service()
        
        # Only initialize if Pinecone is available and configured
        if not PINECONE_AVAILABLE:
            print("Vector DB disabled: pinecone not installed")
            return
            
        if not Config.PINECONE_API_KEY:
            print("Vector DB disabled: PINECONE_API_KEY not set")
            return
        
        try:
            # Initialize Pinecone
            self.pc = Pinecone(api_key=Config.PINECONE_API_KEY)
            
            # Create index if it doesn't exist
            existing_indexes = [index.name for index in self.pc.list_indexes()]
            
            if Config.PINECONE_INDEX_NAME not in existing_indexes:
                print(f"Creating Pinecone index: {Config.PINECONE_INDEX_NAME}")
                self.pc.create_index(
                    name=Config.PINECONE_INDEX_NAME,
                    dimension=Config.EMBEDDING_DIMENSION,
                    metric='cosine',
                    spec=ServerlessSpec(
                        cloud='aws',
                        region=Config.PINECONE_ENVIRONMENT
                    )
                )
            
            # Connect to index
            self.index = self.pc.Index(Config.PINECONE_INDEX_NAME)
            self.enabled = True
            print(f"✅ Vector DB enabled: Connected to {Config.PINECONE_INDEX_NAME}")
            
        except Exception as e:
            print(f"❌ Vector DB initialization failed: {e}")
            self.enabled = False
    
    def is_enabled(self) -> bool:
        """Check if vector database is available."""
        return self.enabled
    
    def store_claim(
        self,
        claim_id: str,
        query: str,
        verdict: str,
        confidence: float,
        summary: str,
        sources: List[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Store a verified claim in the vector database.
        
        Args:
            claim_id: Unique identifier for the claim
            query: Original user query/claim
            verdict: Verdict (TRUE/FALSE/MISLEADING/UNVERIFIED/COMPLEX)
            confidence: Confidence score (0-1)
            summary: Brief explanation
            sources: List of source information
            metadata: Additional metadata
            
        Returns:
            True if stored successfully, False otherwise
        """
        if not self.enabled:
            print(f"⚠️  Vector DB not enabled, skipping storage for: {query[:50]}...")
            return False
        
        try:
            print(f"💾 Attempting to store claim: {claim_id}")
            print(f"   Query: {query[:80]}...")
            
            # Generate embedding for the query
            embedding = self.embedding_service.embed_text(query)
            print(f"   Generated embedding with {len(embedding)} dimensions")
            
            # Prepare metadata
            claim_metadata = {
                "query": query[:500],  # Limit query length for metadata
                "verdict": verdict,
                "confidence": float(confidence),
                "summary": summary[:1000],  # Limit summary length
                "source_count": len(sources),
                "timestamp": datetime.utcnow().isoformat(),
                **(metadata or {})
            }
            
            # Store first 3 sources (Pinecone has metadata size limits)
            for i, source in enumerate(sources[:3]):
                claim_metadata[f"source_{i}_url"] = str(source.get("url", ""))[:500]
                claim_metadata[f"source_{i}_title"] = str(source.get("title", ""))[:200]
            
            print(f"   Prepared metadata with {len(claim_metadata)} fields")
            
            # Upsert to Pinecone
            self.index.upsert(
                vectors=[
                    {
                        "id": claim_id,
                        "values": embedding,
                        "metadata": claim_metadata
                    }
                ]
            )
            
            print(f"✅ Successfully stored claim {claim_id} in vector DB")
            return True
            
        except Exception as e:
            print(f"❌ Error storing claim in vector DB: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def query_similar_claims(
        self,
        query: str,
        top_k: int = None,
        min_score: float = None
    ) -> List[Dict[str, Any]]:
        """
        Find similar claims in the vector database.
        
        Args:
            query: User query to search for
            top_k: Number of results to return (default: from config)
            min_score: Minimum similarity score (default: from config)
            
        Returns:
            List of similar claims with metadata and similarity scores
        """
        if not self.enabled:
            return []
        
        try:
            # Generate embedding for query
            embedding = self.embedding_service.embed_text(query)
            
            # Query Pinecone
            top_k = top_k or Config.VECTOR_TOP_K
            results = self.index.query(
                vector=embedding,
                top_k=top_k,
                include_metadata=True
            )
            
            # Filter by minimum score
            min_score = min_score or Config.VECTOR_SIMILARITY_THRESHOLD
            similar_claims = []
            
            for match in results.matches:
                if match.score >= min_score:
                    similar_claims.append({
                        "id": match.id,
                        "score": match.score,
                        "metadata": match.metadata
                    })
            
            return similar_claims
            
        except Exception as e:
            print(f"Error querying vector DB: {e}")
            return []
    
    def get_best_match(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Get the best matching claim if it meets confidence threshold.
        
        Args:
            query: User query
            
        Returns:
            Best match dict or None if no confident match
        """
        results = self.query_similar_claims(query, top_k=1)
        
        if results and results[0]["score"] >= Config.VECTOR_SIMILARITY_THRESHOLD:
            return results[0]
        
        return None
    
    def delete_claim(self, claim_id: str) -> bool:
        """
        Delete a claim from the vector database.
        
        Args:
            claim_id: ID of claim to delete
            
        Returns:
            True if deleted successfully
        """
        if not self.enabled:
            return False
        
        try:
            self.index.delete(ids=[claim_id])
            return True
        except Exception as e:
            print(f"Error deleting claim: {e}")
            return False


# Singleton instance
_vector_service = None

def get_vector_service() -> VectorService:
    """Get or create singleton vector service instance."""
    global _vector_service
    if _vector_service is None:
        _vector_service = VectorService()
    return _vector_service
