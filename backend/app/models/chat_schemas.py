from pydantic import BaseModel, Field
from typing import List, Optional

class ChatMessage(BaseModel):
    """Single chat message"""
    role: str = Field(..., description="user or assistant")
    content: str = Field(..., description="Message content")

class ChatSource(BaseModel):
    """Source citation from grounded search"""
    url: str
    title: Optional[str] = None
    snippet: Optional[str] = None

class ChatRequest(BaseModel):
    """Chat request with optional conversation history"""
    message: str = Field(..., description="User's message")
    conversation_history: List[ChatMessage] = Field(default_factory=list, description="Previous messages")

class ChatResponse(BaseModel):
    """Chat response with sources"""
    response: str = Field(..., description="AI assistant's response")
    sources: List[ChatSource] = Field(default_factory=list, description="Grounded search sources")
    has_grounding: bool = Field(default=False, description="Whether response used grounded search")
