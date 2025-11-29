"""
Pydantic models for deep research system
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

# Enums
class ClaimType(str, Enum):
    POLICY_ANNOUNCEMENT = "policy_announcement"
    FACTUAL_CLAIM = "factual_claim"
    PREDICTION = "prediction"
    OPINION = "opinion"
    MIXED = "mixed"

class UrgencyLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class Verdict(str, Enum):
    CONFIRMED_TRUE = "CONFIRMED_TRUE"
    LIKELY_TRUE = "LIKELY_TRUE"
    UNCERTAIN = "UNCERTAIN"
    LIKELY_FALSE = "LIKELY_FALSE"
    CONFIRMED_FALSE = "CONFIRMED_FALSE"

class SourceType(str, Enum):
    OFFICIAL = "official_source"
    NEWS = "news_media"
    FACT_CHECKER = "fact_checker"
    ACADEMIC = "academic"
    SOCIAL = "social_media"
    UNKNOWN = "unknown"

# Agent 1 Models
class Entities(BaseModel):
    actors: List[str] = Field(default_factory=list, description="Who is involved")
    actions: List[str] = Field(default_factory=list, description="What is happening")
    objects: List[str] = Field(default_factory=list, description="What is being acted upon")
    temporal: List[str] = Field(default_factory=list, description="When (dates, times)")
    geographic: List[str] = Field(default_factory=list, description="Where (locations)")

class StructuredClaim(BaseModel):
    original_claim: str = Field(..., description="Original user input")
    entities: Entities
    claim_type: ClaimType
    urgency: UrgencyLevel
    extracted_at: datetime = Field(default_factory=datetime.now)

# Agent 2 Models
class SearchResult(BaseModel):
    url: str
    title: str
    snippet: Optional[str] = None
    date: Optional[str] = None
    source_type: SourceType = SourceType.UNKNOWN
    relevance_score: float = Field(ge=0.0, le=1.0)

class SourceFinderOutput(BaseModel):
    search_queries: List[str]
    sources: List[SearchResult]
    total_found: int

# Agent 3 Models
class ResearchQuestion(BaseModel):
    question: str
    priority: int = Field(ge=1, le=10)
    rationale: str

class PlanningOutput(BaseModel):
    research_questions: List[ResearchQuestion]
    identified_gaps: List[str]
    estimated_time: Optional[int] = None  # in seconds

# Agent 4 Models
class ResearchFinding(BaseModel):
    source_url: str
    excerpt: str
    relevance: float
    credibility_score: float
    timestamp: Optional[str] = None

class ParallelResearchOutput(BaseModel):
    question: str
    findings: List[ResearchFinding]
    summary: str
    confidence: float

# Agent 5 Models
class TimelineEvent(BaseModel):
    date: str
    event: str
    source: str
    importance: int = Field(ge=1, le=10)

class KnowledgeGraph(BaseModel):
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]

class AggregatedData(BaseModel):
    unique_facts: List[str]
    timeline: List[TimelineEvent]
    knowledge_graph: KnowledgeGraph
    credibility_map: Dict[str, float]

# Agent 6 Models
class Evidence(BaseModel):
    supporting: List[str]
    contradicting: List[str]
    
class AnalysisOutput(BaseModel):
    verdict: Verdict
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str
    evidence: Evidence
    red_flags: List[str]
    consensus_view: str

# Agent 7 Models
class Report(BaseModel):
    title: str
    executive_summary: str
    claim: str
    verdict: Verdict
    confidence: float
    key_findings: List[str]
    evidence_analysis: str
    timeline: List[TimelineEvent]
    source_evaluation: str
    conclusion: str
    sources_bibliography: List[SearchResult]
    generated_at: datetime = Field(default_factory=datetime.now)

# Agent 9 Models
class ChatMessage(BaseModel):
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)

class ChatResponse(BaseModel):
    answer: str
    sources: List[str]
    confidence: float
