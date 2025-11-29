"""
Agent 3: Planning Agent
Analyzes initial results and generates research strategy
"""

import json
from typing import List
from loguru import logger
import google.generativeai as genai

from config.settings import Settings
from config.prompts import PLANNING_AGENT_PROMPT
from models.schemas import SourceFinderOutput, PlanningOutput, ResearchQuestion

# Configure Gemini
genai.configure(api_key=Settings.GOOGLE_API_KEY)

class PlanningAgent:
    """
    Agent 3: The Brain - Plans the deep research strategy
    
    Capabilities:
    - Analyze initial search results
    - Identify information gaps
    - Detect contradictions
    - Generate targeted research questions
    - Prioritize tasks
    """
    
    def __init__(self):
        self.model = genai.GenerativeModel(
            model_name=Settings.DEFAULT_MODEL,
            generation_config={
                "temperature": Settings.TEMPERATURE,
                "max_output_tokens": Settings.MAX_TOKENS,
            }
        )
        logger.info("PlanningAgent initialized")

    def create_plan(self, source_output: SourceFinderOutput) -> PlanningOutput:
        """
        Create research plan based on initial findings
        
        Args:
            source_output: Output from Agent 2
            
        Returns:
            PlanningOutput with research questions and gaps
        """
        logger.info("Creating research plan...")
        
        # Prepare context from search results
        results_summary = []
        for s in source_output.sources[:10]: # Analyze top 10 sources
            results_summary.append(f"- [{s.source_type.value}] {s.title}: {s.snippet}")
            
        context = "\n".join(results_summary)
        
        try:
            # Generate Plan
            prompt = PLANNING_AGENT_PROMPT.format(initial_results=context)
            
            # Add JSON guidance
            prompt += "\n\nReturn ONLY a valid JSON object with this structure:\n"
            prompt += json.dumps({
                "research_questions": [
                    {
                        "question": "string",
                        "priority": 1,
                        "rationale": "string"
                    }
                ],
                "identified_gaps": ["list of strings"],
                "estimated_time": 300
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
            questions = [ResearchQuestion(**q) for q in parsed["research_questions"]]
            
            return PlanningOutput(
                research_questions=questions,
                identified_gaps=parsed.get("identified_gaps", []),
                estimated_time=parsed.get("estimated_time", 300)
            )
            
        except Exception as e:
            logger.error(f"Error creating plan: {e}")
            # Fallback plan
            return self._create_fallback_plan()

    def _create_fallback_plan(self) -> PlanningOutput:
        """Create basic plan if LLM fails"""
        return PlanningOutput(
            research_questions=[
                ResearchQuestion(
                    question="Verify the main claim with official sources",
                    priority=1,
                    rationale="Fallback: Basic verification needed"
                )
            ],
            identified_gaps=["Unable to analyze gaps due to error"],
            estimated_time=60
        )

if __name__ == "__main__":
    # Test
    agent = PlanningAgent()
    # Mock input would go here
