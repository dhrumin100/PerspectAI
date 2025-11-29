"""
Agent 9: Chat Interface Agent (RAG)
Interactive Q&A using LlamaIndex
"""

import os
from typing import List
from loguru import logger
from llama_index.core import VectorStoreIndex, Document, Settings as LlamaSettings
from llama_index.llms.gemini import Gemini
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

from config.settings import Settings
from models.schemas import Report, ChatResponse

# Configure LlamaIndex with Gemini API
LlamaSettings.llm = Gemini(
    api_key=Settings.GOOGLE_API_KEY, 
    model_name=Settings.DEFAULT_MODEL,  # gemini-2.0-flash-exp
    temperature=Settings.TEMPERATURE,
    max_tokens=Settings.MAX_TOKENS
)
LlamaSettings.embed_model = HuggingFaceEmbedding(model_name=Settings.EMBEDDING_MODEL)

class ChatInterfaceAgent:
    """
    Agent 9: The Guide - Interactive RAG interface
    
    Capabilities:
    - Index report content
    - Answer user questions
    - Cite sources
    """
    
    def __init__(self):
        self.index = None
        self.query_engine = None
        logger.info("ChatInterfaceAgent initialized")

    def load_report(self, report: Report):
        """
        Load report into vector index
        
        Args:
            report: Generated report object
        """
        logger.info("Indexing report...")
        
        # Create documents from report sections
        documents = [
            Document(text=report.executive_summary, metadata={"section": "Executive Summary"}),
            Document(text=report.evidence_analysis, metadata={"section": "Evidence Analysis"}),
            Document(text=report.source_evaluation, metadata={"section": "Source Evaluation"}),
            Document(text=report.conclusion, metadata={"section": "Conclusion"}),
        ]
        
        # Add key findings
        for finding in report.key_findings:
            documents.append(Document(text=finding, metadata={"section": "Key Findings"}))
            
        # Build Index
        self.index = VectorStoreIndex.from_documents(documents)
        self.query_engine = self.index.as_query_engine()
        logger.info("Report indexed successfully")

    def chat(self, question: str) -> ChatResponse:
        """
        Answer user question based on report
        
        Args:
            question: User query
            
        Returns:
            ChatResponse with answer and sources
        """
        if not self.query_engine:
            return ChatResponse(
                answer="Please load a report first.",
                sources=[],
                confidence=0.0
            )
            
        logger.info(f"Answering: {question}")
        
        try:
            response = self.query_engine.query(question)
            
            return ChatResponse(
                answer=str(response),
                sources=[node.metadata.get("section", "Unknown") for node in response.source_nodes],
                confidence=0.9 # Placeholder
            )
            
        except Exception as e:
            logger.error(f"Error in chat: {e}")
            return ChatResponse(
                answer="I encountered an error answering that.",
                sources=[],
                confidence=0.0
            )

if __name__ == "__main__":
    pass
