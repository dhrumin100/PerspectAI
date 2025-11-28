"""
Parser for enhanced structured verdict responses
"""
import json
import re
from datetime import datetime
from typing import Dict, Optional
from app.models.schemas import StructuredVerdict, EvidenceItem, Evidence, Provenance, VerdictType


class VerdictParser:
    """Parse and validate structured verdict responses from Gemini"""
    
    @staticmethod
    def parse(response_text: str) -> Dict:
        """
        Parse JSON + summary format from Gemini response
        
        Expected format:
        {JSON object}
        
        Short summary: One line text
        
        Returns:
            Dict with 'verdict_data' (StructuredVerdict fields) and 'ui_summary' (str)
        """
        try:
            # Split on double newline
            parts = response_text.split('\n\n')
            
            json_part = ""
            summary_part = ""
            
            # Find JSON part and summary part
            for i, part in enumerate(parts):
                part_stripped = part.strip()
                
                # Check if this looks like JSON
                if part_stripped.startswith('{') or '```json' in part_stripped or '```' in part_stripped:
                    json_part = part_stripped
                    # Look for summary in remaining parts
                    if i + 1 < len(parts):
                        for remaining in parts[i+1:]:
                            if 'Short summary:' in remaining or 'summary:' in remaining.lower():
                                summary_part = remaining.strip()
                                break
                    break
            
            if not json_part:
                raise ValueError("No JSON found in response")
            
            # Extract JSON (remove markdown if present)
            if '```json' in json_part:
                json_part = json_part.split('```json')[1].split('```')[0].strip()
            elif '```' in json_part:
                json_part = json_part.split('```')[1].split('```')[0].strip()
            
            # Parse JSON
            verdict_dict = json.loads(json_part)
            
            # Extract UI summary if present
            ui_summary = ""
            if summary_part:
                # Remove "Short summary:" prefix
                ui_summary = re.sub(r'^Short summary:\s*', '', summary_part, flags=re.IGNORECASE).strip()
            
            # Validate required fields
            required_fields = ['verdict', 'confidence', 'summary', 'reasoning', 'evidence', 'provenance']
            missing = [f for f in required_fields if f not in verdict_dict]
            if missing:
                raise ValueError(f"Missing required fields: {missing}")
            
            # Validate verdict value
            verdict_str = verdict_dict['verdict'].upper()
            try:
                VerdictType(verdict_str)
                verdict_dict['verdict'] = verdict_str
            except ValueError:
                print(f"Invalid verdict '{verdict_str}', defaulting to UNVERIFIED")
                verdict_dict['verdict'] = "UNVERIFIED"
            
            # Add UI summary to dict
            verdict_dict['ui_summary'] = ui_summary or verdict_dict['summary']
            
            # Ensure timestamp exists
            if 'timestamp' not in verdict_dict or not verdict_dict['timestamp']:
                verdict_dict['timestamp'] = datetime.utcnow().isoformat() + 'Z'
            
            return verdict_dict
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON parse error: {e}")
            raise ValueError(f"Failed to parse JSON verdict: {e}")
        except Exception as e:
            print(f"❌ Verdict parsing error: {e}")
            raise ValueError(f"Failed to parse verdict response: {e}")
    
    @staticmethod
    def create_fallback_verdict(
        query: str, 
        context: str = "",
        reason: str = "Error processing claim"
    ) -> Dict:
        """
        Create a fallback UNVERIFIED verdict when parsing fails
        
        Args:
            query: Original user query
            context: Search context (optional)
            reason: Reason for fallback
            
        Returns:
            Dict with minimal verdict structure
        """
        return {
            "verdict": "UNVERIFIED",
            "confidence": 0.3,
            "summary": f"{reason}. Unable to verify: {query[:100]}",
            "reasoning": [
                "Step 1: Attempted to analyze the claim",
                f"Step 2: {reason}",
                "Step 3: Defaulting to UNVERIFIED due to processing error"
            ],
            "evidence": {
                "supporting": [],
                "contradicting": [],
                "neutral": []
            },
            "provenance": {
                "sources_considered": [],
                "primary_source": None,
                "search_method": "ERROR"
            },
            "actionable_recommendation": "Please try rephrasing your question or try again later.",
            "timestamp": datetime.utcnow().isoformat() + 'Z',
            "ui_summary": f"Could not verify this claim: {reason}"
        }
    
    @staticmethod
    def validate_schema(verdict_dict: Dict) -> bool:
        """
        Validate that a verdict dict matches the expected schema
        
        Returns:
            True if valid, False otherwise
        """
        try:
            # Try to create StructuredVerdict object (will raise if invalid)
            StructuredVerdict(**verdict_dict)
            return True
        except Exception as e:
            print(f"Schema validation failed: {e}")
            return False
