"""
Agent 6: Analysis & Reasoning Agent
Analyzes knowledge base to generate verdicts and reasoning
"""

import json
from typing import List, Dict, Any
from loguru import logger
import google.generativeai as genai

from config.settings import Settings
from config.prompts import ANALYSIS_PROMPT
from models.schemas import (
    AggregatedData, AnalysisOutput, Verdict, Evidence
)

# Configure Gemini
genai.configure(api_key=Settings.GOOGLE_API_KEY)

class AnalysisReasoningAgent:
    """
    Agent 6: The Judge - Analyzes evidence and renders a verdict
    
    Capabilities:
    - Detect contradictions
    - Evaluate consensus
    - Generate verdict
    - Calculate confidence score
    - Provide detailed reasoning
    """
    
    def __init__(self):
        self.model = genai.GenerativeModel(
            model_name=Settings.DEFAULT_MODEL,
            generation_config={
                "temperature": Settings.TEMPERATURE,
                "max_output_tokens": Settings.MAX_TOKENS,
            }
        )
        logger.info("AnalysisReasoningAgent initialized")

    def analyze_claim(self, claim: str, data: AggregatedData) -> AnalysisOutput:
        """
        Analyze claim against aggregated data
        
        Args:
            claim: Original user claim
            data: Aggregated knowledge base from Agent 5
            
        Returns:
            AnalysisOutput with verdict and reasoning
        """
        logger.info(f"Analyzing claim: {claim[:50]}...")
        
        # Prepare context
        facts = "\n".join([f"- {f}" for f in data.unique_facts])
        timeline = "\n".join([f"- {t.date}: {t.event}" for t in data.timeline])
        
        context = f"""
        Facts:
        {facts}
        
        Timeline:
        {timeline}
        
        Credibility Map:
        {json.dumps(data.credibility_map, indent=2)}
        """
        
        try:
            # Generate Analysis
            prompt = ANALYSIS_PROMPT.format(
                knowledge_base=context,
                claim=claim
            )
            
            # Add JSON guidance
            prompt += "\n\nReturn ONLY a valid JSON object with this structure:\n"
            prompt += json.dumps({
                "verdict": "CONFIRMED_TRUE|LIKELY_TRUE|UNCERTAIN|LIKELY_FALSE|CONFIRMED_FALSE",
                "confidence": 0.85,
                "reasoning": "string",
                "evidence": {
                    "supporting": ["list of strings"],
                    "contradicting": ["list of strings"]
                },
                "red_flags": ["list of strings"],
                "consensus_view": "string"
            }, indent=2)
            
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            
            # Extract JSON
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
                
            parsed = json.loads(text)
            
            return AnalysisOutput(
                verdict=Verdict(parsed["verdict"]),
                confidence=float(parsed["confidence"]),
                reasoning=parsed["reasoning"],
                evidence=Evidence(**parsed["evidence"]),
                red_flags=parsed.get("red_flags", []),
                consensus_view=parsed.get("consensus_view", "Unknown")
            )
            
        except Exception as e:
            logger.error(f"Error analyzing claim: {e}")
            return self._create_fallback_analysis()

    def _create_fallback_analysis(self) -> AnalysisOutput:
        """Create basic analysis if LLM fails"""
        return AnalysisOutput(
            verdict=Verdict.UNCERTAIN,
            confidence=0.0,
            reasoning="Error during analysis phase.",
            evidence=Evidence(supporting=[], contradicting=[]),
            red_flags=["Analysis failed"],
            consensus_view="Unknown"
        )

if __name__ == "__main__":
    pass
