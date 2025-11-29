"""
Agent 5: Data Aggregator
Aggregates findings, builds knowledge graph and timeline
"""

import json
import networkx as nx
from typing import List, Dict, Any
from loguru import logger
import google.generativeai as genai

from config.settings import Settings
from config.prompts import AGGREGATION_PROMPT
from models.schemas import (
    ParallelResearchOutput, AggregatedData, 
    TimelineEvent, KnowledgeGraph
)

# Configure Gemini
genai.configure(api_key=Settings.GOOGLE_API_KEY)

class DataAggregatorAgent:
    """
    Agent 5: Synthesizes research data into structured knowledge
    
    Capabilities:
    - Deduplicate facts
    - Build timeline
    - Construct knowledge graph
    - Score credibility
    """
    
    def __init__(self):
        self.model = genai.GenerativeModel(
            model_name=Settings.DEFAULT_MODEL,
            generation_config={
                "temperature": Settings.TEMPERATURE,
                "max_output_tokens": Settings.MAX_TOKENS,
            }
        )
        logger.info("DataAggregatorAgent initialized")

    def aggregate_data(self, research_outputs: List[ParallelResearchOutput]) -> AggregatedData:
        """
        Aggregate research findings into knowledge base
        
        Args:
            research_outputs: List of outputs from Agent 4
            
        Returns:
            AggregatedData with graph and timeline
        """
        logger.info("Aggregating research data...")
        
        # Prepare context
        all_findings = []
        for out in research_outputs:
            for f in out.findings:
                all_findings.append(f"- {f.excerpt} (Source: {f.source_url})")
        
        context = "\n".join(all_findings)
        
        try:
            # Generate Aggregation
            prompt = AGGREGATION_PROMPT.format(all_results=context)
            
            # Add JSON guidance
            prompt += "\n\nReturn ONLY a valid JSON object with this structure:\n"
            prompt += json.dumps({
                "unique_facts": ["list of strings"],
                "timeline": [
                    {
                        "date": "YYYY-MM-DD",
                        "event": "string",
                        "source": "string",
                        "importance": 1
                    }
                ],
                "knowledge_graph": {
                    "nodes": [{"id": "string", "label": "string", "type": "string"}],
                    "edges": [{"source": "string", "target": "string", "relation": "string"}]
                },
                "credibility_map": {"source_name": 0.9}
            }, indent=2)
            
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            
            # Extract JSON
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
                
            parsed = json.loads(text)
            
            # Convert to Pydantic models
            timeline = [TimelineEvent(**t) for t in parsed.get("timeline", [])]
            
            kg_data = parsed.get("knowledge_graph", {"nodes": [], "edges": []})
            kg = KnowledgeGraph(
                nodes=kg_data.get("nodes", []),
                edges=kg_data.get("edges", [])
            )
            
            return AggregatedData(
                unique_facts=parsed.get("unique_facts", []),
                timeline=timeline,
                knowledge_graph=kg,
                credibility_map=parsed.get("credibility_map", {})
            )
            
        except Exception as e:
            logger.error(f"Error aggregating data: {e}")
            return self._create_fallback_data()

    def _create_fallback_data(self) -> AggregatedData:
        """Create basic data if LLM fails"""
        return AggregatedData(
            unique_facts=["Error in aggregation"],
            timeline=[],
            knowledge_graph=KnowledgeGraph(nodes=[], edges=[]),
            credibility_map={}
        )

if __name__ == "__main__":
    pass
