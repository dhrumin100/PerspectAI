"""
Agent 1: Query Analyzer
Extracts and structures user claims for fact-checking
"""

import json
import google.generativeai as genai
from typing import Dict, Any
from loguru import logger

from config.settings import Settings
from config.prompts import QUERY_ANALYZER_PROMPT
from models.schemas import StructuredClaim, Entities, ClaimType, UrgencyLevel

# Configure Gemini
genai.configure(api_key=Settings.GOOGLE_API_KEY)


class QueryAnalyzerAgent:
    """
    Agent 1: Analyzes user input and extracts structured information
    
    Capabilities:
    - Parse text/voice/image input
    - Extract named entities
    - Identify claim type
    - Assess urgency
    """
    
    def __init__(self):
        self.model = genai.GenerativeModel(
            model_name=Settings.DEFAULT_MODEL,
            generation_config={
                "temperature": Settings.TEMPERATURE,
                "max_output_tokens": Settings.MAX_TOKENS,
            }
        )
        logger.info("QueryAnalyzerAgent initialized")
    
    def analyze(self, user_input: str) -> StructuredClaim:
        """
        Analyze user input and return structured claim
        
        Args:
            user_input: Raw user query/claim
            
        Returns:
            StructuredClaim with extracted entities and metadata
        """
        try:
            logger.info(f"Analyzing claim: {user_input[:100]}...")
            
            # Create prompt
            prompt = QUERY_ANALYZER_PROMPT.format(user_input=user_input)
            
            # Add JSON schema guidance
            prompt += "\n\nReturn ONLY a valid JSON object with this structure:\n"
            prompt += json.dumps({
                "original_claim": "string",
                "entities": {
                    "actors": ["list of strings"],
                    "actions": ["list of strings"],
                    "objects": ["list of strings"],
                    "temporal": ["list of strings"],
                    "geographic": ["list of strings"]
                },
                "claim_type": "policy_announcement|factual_claim|prediction|opinion|mixed",
                "urgency": "low|medium|high"
            }, indent=2)
            
            # Call LLM
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Extract JSON from response (handle markdown code blocks)
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            # Parse JSON
            parsed = json.loads(response_text)
            
            # Create structured claim
            structured_claim = StructuredClaim(
                original_claim=parsed["original_claim"],
                entities=Entities(**parsed["entities"]),
                claim_type=ClaimType(parsed["claim_type"]),
                urgency=UrgencyLevel(parsed["urgency"])
            )
            
            logger.success(f"Successfully analyzed claim. Type: {structured_claim.claim_type}")
            return structured_claim
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            logger.error(f"Response was: {response_text}")
            # Fallback: create basic structured claim
            return self._create_fallback_claim(user_input)
        
        except Exception as e:
            logger.error(f"Error in query analysis: {e}")
            return self._create_fallback_claim(user_input)
    
    def _create_fallback_claim(self, user_input: str) -> StructuredClaim:
        """Create a basic structured claim when LLM fails"""
        return StructuredClaim(
            original_claim=user_input,
            entities=Entities(),
            claim_type=ClaimType.FACTUAL_CLAIM,
            urgency=UrgencyLevel.MEDIUM
        )
    
    def extract_entities_simple(self, text: str) -> Dict[str, Any]:
        """
        Simple keyword-based entity extraction (fallback)
        Can be enhanced with spaCy in future
        """
        # This is a placeholder for more sophisticated NER
        # In production, use spaCy or similar
        return {
            "actors": [],
            "actions": [],
            "objects": [],
            "temporal": [],
            "geographic": []
        }


# Example usage
if __name__ == "__main__":
    agent = QueryAnalyzerAgent()
    
    # Test claims
    test_claims = [
        "India will ban XYZ platform next week",
        "The Earth is flat",
        "Climate change is causing more hurricanes"
    ]
    
    for claim in test_claims:
        print(f"\n{'='*60}")
        print(f"Input: {claim}")
        result = agent.analyze(claim)
        print(f"\nOutput:")
        print(json.dumps(result.model_dump(), indent=2, default=str))
