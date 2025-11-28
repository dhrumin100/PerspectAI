"""
Pydantic models for API request/response schemas
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum


class VerdictType(str, Enum):
    """Possible verdicts for fact-checking"""
    TRUE = "TRUE"
    FALSE = "FALSE"
    MISLEADING = "MISLEADING"
    UNVERIFIED = "UNVERIFIED"
    COMPLEX = "COMPLEX"


class IntentType(str, Enum):
    """Types of user intents"""
    FACT_CHECK = "FACT_CHECK"
    CRISIS = "CRISIS"
    GENERAL = "GENERAL"
    ARCHIVE = "ARCHIVE"


class SourceInfo(BaseModel):
    """Information about a source"""
    url: str
    title: str
    credibility: str = Field(default="medium", description="high, medium, or low")
    date: Optional[str] = None
    excerpt: Optional[str] = None


class EvidenceItem(BaseModel):
    """Single piece of evidence with credibility scoring"""
    title: str = Field(..., description="Source title")
    url: str = Field(..., description="Source URL")
    excerpt: str = Field(..., max_length=200, description="Short excerpt from source")
    credibility_score: float = Field(..., ge=0.0, le=1.0, description="0-1 credibility score based on source reputation")


class Evidence(BaseModel):
    """Evidence breakdown with structured items"""
    supporting: List[EvidenceItem] = Field(default_factory=list)
    contradicting: List[EvidenceItem] = Field(default_factory=list)
    neutral: List[EvidenceItem] = Field(default_factory=list)


class Provenance(BaseModel):
    """Source tracking and search method metadata"""
    sources_considered: List[str] = Field(default_factory=list, description="All URLs considered during search")
    primary_source: Optional[str] = Field(None, description="Most credible/relevant source")
    search_method: str = Field(..., description="How data was obtained: GROUNDED_SEARCH, CACHED, VECTOR_DB")


class StructuredVerdict(BaseModel):
    """Enhanced verdict with full structured schema"""
    verdict: VerdictType
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score 0-1")
    summary: str = Field(..., min_length=10, max_length=500, description="Natural language summary of verdict")
    reasoning: List[str] = Field(..., min_items=1, description="Step-by-step reasoning process")
    evidence: Evidence
    provenance: Provenance
    actionable_recommendation: str = Field(..., max_length=300, description="What user should do next")
    timestamp: str = Field(..., description="UTC timestamp of analysis")
    ui_summary: Optional[str] = Field(None, description="One-line summary for frontend display")


class QueryRequest(BaseModel):
    """User query request"""
    query: str = Field(..., description="The claim or question to verify")
    use_vector_db: bool = Field(default=True, description="Whether to use vector database")
    require_web_search: bool = Field(default=False, description="Force web search even if vector DB has results")


class QueryResponse(BaseModel):
    """Enhanced response for fact-checking"""
    intent: IntentType
    verdict: Optional[VerdictType] = None
    confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Confidence score 0-1")
    summary: str = Field(..., description="Brief explanation of the verdict")
    evidence: Optional[Evidence] = None
    sources: List[SourceInfo] = Field(default_factory=list)
    search_used: str = Field(default="llm", description="vector_db, web_search, both, or llm")
    processing_time_ms: Optional[int] = None


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    services: Dict[str, str]
