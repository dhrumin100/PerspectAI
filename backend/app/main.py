from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import time
from app.agents.rapid_agent import RapidAgent
from app.models.schemas import QueryRequest, QueryResponse, HealthResponse
from app.models.chat_schemas import ChatRequest, ChatResponse, ChatSource
from app.utils.structured_logger import logger
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

app = FastAPI(
    title="PerspectAI API",
    version="1.0.0",
    description="AI-powered fact-checking and misinformation detection system"
)

# Rate Limiter
limiter = Limiter(key_func=get_remote_address)

# Allow CORS for Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add rate limit exceeded handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Initialize Agent
agent = RapidAgent()


@app.get("/", response_model=HealthResponse)
def read_root():
    """Health check endpoint"""
    return HealthResponse(
        status="online",
        version="1.0.0",
        services={
            "rapid_agent": "online",
            "search_service": "online"
        }
    )


@app.get("/health", response_model=HealthResponse)
def health_check():
    """Detailed health check"""
    from app.services.vector_service import get_vector_service
    vector_service = get_vector_service()
    
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        services={
            "rapid_agent": "online",
            "search_service": "online",
            "vector_db": "online" if vector_service.is_enabled() else "disabled"
        }
    )


@app.post("/api/verify", response_model=QueryResponse)
def verify_claim(request: QueryRequest):
    """
    Verify a claim or fact-check a statement.
    
    This is the main endpoint for the Rapid AI Layer (Component 1).
    Enhanced with vector database, structured responses, and source parsing.
    """
    try:
        start_time = time.time()
        
        # Process request through enhanced rapid agent
        response = agent.process_request(request.query)
        
        # Add processing time
        processing_time = int((time.time() - start_time) * 1000)
        response.processing_time_ms = processing_time
        
        return response
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/chat", response_model=ChatResponse)
@limiter.limit("10/minute")  # Rate limit: 10 requests per minute
def chat(request: Request, chat_request: ChatRequest):
    """
    Chat endpoint - uses enhanced rapid agent for ALL queries.
    Provides consistent responses with vector DB caching.
    """
    start_time = time.time()
    
    try:
        print(f"📨 Chat request: {chat_request.message[:100]}...")
        
        # Log incoming request
        logger.log_request(
            query=chat_request.message,
            intent="unknown",  # Will be determined by agent
            cache_hit=False  # Will be updated
        )
        
        # Use enhanced rapid agent for ALL queries
        result = agent.process_request(chat_request.message)
        
        print(f"   Summary length: {len(result.summary) if result.summary else 0}")
        print(f"   Sources: {len(result.sources)}")
        
        # Log verdict generation
        if result.verdict:
            logger.log_verdict(
                verdict=result.verdict.value,
                confidence=result.confidence,
                sources_count=len(result.sources),
                search_method=result.search_used
            )
        
        # Format response text
        response_text = format_query_response_as_chat(result)
        
        print(f"✅ Response text length: {len(response_text)}")
        
        # Convert sources
        sources = [
            ChatSource(
                url=source.url,
                title=source.title or "Source",
                snippet=source.excerpt
            )
            for source in result.sources
        ]
        
        # Log performance
        duration_ms = int((time.time() - start_time) * 1000)
        logger.log_performance(
            operation="chat_request",
            duration_ms=duration_ms,
            cache_hit=(result.search_used == "vector_db"),
            sources_count=len(sources)
        )
        
        return ChatResponse(
            response=response_text,
            sources=sources,
            has_grounding=len(sources) > 0
        )
        
    except Exception as e:
        duration_ms = int((time.time() - start_time) * 1000)
        print(f"❌ ERROR in chat: {e}")
        
        # Log error with context
        logger.log_error(
            error=str(e),
            context={
                "query": chat_request.message[:100],
                "duration_ms": duration_ms
            }
        )
        
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Error processing request: {str(e)}"
        )


def format_query_response_as_chat(query_response: QueryResponse) -> str:
    """Format QueryResponse into chat message with verdict, confidence, summary."""
    parts = []
    
    # Add verdict badge if available
    if query_response.verdict:
        verdict_emoji = {
            "TRUE": "✅",
            "FALSE": "❌",
            "MISLEADING": "⚠️",
            "UNVERIFIED": "❓",
            "COMPLEX": "🔄"
        }
        emoji = verdict_emoji.get(query_response.verdict.value, "")
        parts.append(f"**Verdict**: {emoji} {query_response.verdict.value}")
    
    # Add confidence
    if query_response.confidence > 0:
        confidence_pct = int(query_response.confidence * 100)
        parts.append(f"**Confidence**: {confidence_pct}%")
    
    # Add summary (CRITICAL - this is the main response text!)
    if query_response.summary:
        parts.append(f"\n{query_response.summary}")
    else:
        parts.append("\nNo summary available.")
    
    # Add evidence
    if query_response.evidence:
        if query_response.evidence.supporting:
            parts.append(f"\n**Supporting Evidence**:")
            for evidence in query_response.evidence.supporting[:2]:
                parts.append(f"• {evidence}")
        
        if query_response.evidence.contradicting:
            parts.append(f"\n**Contradicting Evidence**:")
            for evidence in query_response.evidence.contradicting[:2]:
                parts.append(f"• {evidence}")
    
    # Cache indicator
    if query_response.search_used == "vector_db":
        parts.append("\n\n_💾 Retrieved from cache_")
    
    return "\n".join(parts)


@app.post("/api/verify-legacy")
def verify_legacy(request: QueryRequest):
    """Legacy verify endpoint"""
    return verify_claim(request)


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
