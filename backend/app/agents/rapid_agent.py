from google import genai
from google.genai import types
from app.core.config import Config
from app.core.prompts import SYSTEM_PERSONA, INTENT_CLASSIFICATION_PROMPT, STRUCTURED_VERDICT_PROMPT, CONVERSATIONAL_CHAT_PROMPT
from app.services.search_service import SearchService
from app.services.vector_service import get_vector_service
from app.models.schemas import QueryResponse, VerdictType, IntentType, Evidence, SourceInfo, EvidenceItem
from app.utils.verdict_parser import VerdictParser
from app.utils.credibility import CredibilityScorer
import json
import hashlib
from typing import Optional
from datetime import datetime


class RapidAgent:
    def __init__(self):
        self.client = genai.Client(api_key=Config.GOOGLE_API_KEY)
        self.model = Config.MODEL_NAME
        self.search_service = SearchService()
        self.vector_service = get_vector_service()
        
        # Initialize model with System Instruction for consistent persona
        self.system_instruction = types.Content(
            role="system",
            parts=[types.Part.from_text(text=SYSTEM_PERSONA)]
        )

    def classify_intent(self, query: str) -> str:
        """
        Classifies the user query using the dedicated prompt.
        """
        formatted_prompt = INTENT_CLASSIFICATION_PROMPT.format(query=query)
        
        response = self.client.models.generate_content(
            model=self.model,
            contents=formatted_prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PERSONA
            )
        )
        return response.text.strip().upper()

    def process_request(self, query: str) -> QueryResponse:
        """
        Main entry point for the Rapid Layer with vector search + structured responses.
        
        Flow:
        1. Classify intent
        2. Check vector DB for similar claims (if enabled)
        3. If confident match found -> return cached result
        4. Otherwise -> perform web search
        5. Synthesize structured response
        6. Store in vector DB for future
        7. Return QueryResponse
        """
        # 1. Classify Intent
        intent_str = self.classify_intent(query)
        print(f"DEBUG: Intent classified as: {intent_str}")
        
        try:
            intent = IntentType(intent_str)
        except ValueError:
            intent = IntentType.GENERAL
        
        # 2. Check Vector DB first (optimization) - now includes GENERAL queries!
        if self.vector_service.is_enabled() and intent in [IntentType.FACT_CHECK, IntentType.CRISIS, IntentType.GENERAL]:
            cached_result = self.vector_service.get_best_match(query)
            
            if cached_result:
                print(f"DEBUG: Found cached result with score {cached_result['score']}")
                return self._build_response_from_cache(cached_result, intent)
        
        # 3. No cache hit - proceed with web search
        if intent in [IntentType.FACT_CHECK, IntentType.CRISIS, IntentType.GENERAL]:
            # Perform search with sources
            search_result = self.search_service.search_with_sources(query)
            
            # Extract response and sources - FIX: use 'text' not 'response'
            search_text = search_result.get("text", "")  # Changed from "response" to "text"
            sources_list = search_result.get("sources", [])
            
            print(f"DEBUG: Got search text length: {len(search_text)}")
            print(f"DEBUG: Got {len(sources_list)} sources")
            
            # 4. Synthesize structured fact-check
            if intent in [IntentType.FACT_CHECK, IntentType.CRISIS]:
                verdict_data = self._synthesize_structured_verdict(query, search_text)
                
                # Parse sources into SourceInfo objects
                source_objects = self._parse_sources(sources_list)
                
                # Build response
                response = QueryResponse(
                    intent=intent,
                    verdict=verdict_data.get("verdict"),
                    confidence=verdict_data.get("confidence", 0.0),
                    summary=verdict_data.get("summary", "Unable to determine verdict"),
                    evidence=Evidence(
                        supporting=verdict_data.get("evidence", {}).get("supporting", []),
                        contradicting=verdict_data.get("evidence", {}).get("contradicting", []),
                        neutral=verdict_data.get("evidence", {}).get("neutral", [])
                    ),
                    sources=source_objects,
                    search_used="web_search"
                )
                
                # Store in vector DB ONLY if NOT a duplicate
                if self.vector_service.is_enabled():
                    # Check for near-duplicate before storing
                    is_duplicate = self._check_for_duplicate(query)
                    
                    if not is_duplicate:
                        print(f"💾 Storing NEW query in vector DB: {query[:60]}...")
                        claim_id = self._generate_claim_id(query)
                        self.vector_service.store_claim(
                            claim_id=claim_id,
                            query=query,
                            verdict=response.verdict.value if response.verdict else "UNVERIFIED",
                            confidence=response.confidence,
                            summary=response.summary,
                            sources=[{
                                "url": s.url,
                                "title": s.title or "",
                                "credibility": s.credibility
                            } for s in source_objects[:3]]
                        )
                    else:
                        print(f"⏭️  Skipping storage - duplicate found (similarity > {Config.VECTOR_DUPLICATE_THRESHOLD})")
                
                return response
            
            else:  # GENERAL - Use conversational response
                # Generate natural conversational response from search context
                conversational_response = self._generate_conversational_response(query, search_text)
                
                # Parse sources
                source_objects = self._parse_sources(sources_list)
                
                # Build response
                response = QueryResponse(
                    intent=intent,
                    summary=conversational_response,
                    sources=source_objects,
                    search_used="web_search"
                )
                
                # Store in vector DB for future queries ONLY if NOT duplicate
                if self.vector_service.is_enabled():
                    is_duplicate = self._check_for_duplicate(query)
                    
                    if not is_duplicate:
                        print(f"💾 Storing NEW general query in vector DB: {query[:60]}...")
                        claim_id = self._generate_claim_id(query)
                        self.vector_service.store_claim(
                            claim_id=claim_id,
                            query=query,
                            verdict="GENERAL",  # Use "GENERAL" as verdict for non-fact-check queries
                            confidence=0.85,  # Default confidence for general queries
                            summary=conversational_response,
                            sources=[{
                                "url": s.url,
                                "title": s.title or "",
                                "credibility": s.credibility
                            } for s in source_objects[:3]]
                        )
                    else:
                        print(f"⏭️  Skipping storage - duplicate found")
                
                return response
                
        elif intent == IntentType.ARCHIVE:
            return QueryResponse(
                intent=intent,
                summary="Archive search is not yet implemented.",
                search_used="llm"
            )
        
        return QueryResponse(
            intent=IntentType.GENERAL,
            summary="Could not understand the request.",
            search_used="llm"
        )

    def _synthesize_structured_verdict(self, query: str, context: str, sources_list: list = None) -> dict:
        """
        Use LLM to generate enhanced structured JSON verdict with credibility scoring.
        
        Returns:
            Dict with enhanced schema including reasoning, provenance, credibility scores
        """
        # Inject timestamp into prompt
        timestamp = datetime.utcnow().isoformat() + 'Z'
        formatted_prompt = STRUCTURED_VERDICT_PROMPT.format(
            query=query,
            context=context,
            timestamp=timestamp
        )
        
        try:
            # Call Gemini with low temperature for consistency
            response = self.client.models.generate_content(
                model=self.model,
                contents=formatted_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PERSONA,
                    temperature=0.15  # Low but not zero for some flexibility
                )
            )
            
            response_text = response.text.strip()
            print(f"🤖 Gemini response length: {len(response_text)} chars")
            
            # Parse using enhanced parser
            verdict_data = VerdictParser.parse(response_text)
            
            # Add credibility scores to evidence if sources provided
            if sources_list:
                verdict_data = self._enhance_with_credibility(verdict_data, sources_list)
            
            print(f"✅ Verdict: {verdict_data['verdict']} (confidence: {verdict_data['confidence']})")
            return verdict_data
            
        except ValueError as e:
            # Parsing failed - retry once with clarifying prompt
            print(f"⚠️  Parse failed: {e}. Retrying with clarification...")
            return self._retry_verdict_parse(query, context, timestamp, str(e))
        
        except Exception as e:
            print(f"❌ ERROR in verdict synthesis: {e}")
            import traceback
            traceback.print_exc()
            return VerdictParser.create_fallback_verdict(
                query=query,
                context=context[:500],
                reason="Error processing claim"
            )

    def _parse_sources(self, sources_list: list) -> list[SourceInfo]:
        """
        Convert raw source dicts to SourceInfo objects with credibility scoring.
        """
        source_objects = []
        
        for source in sources_list:
            url = source.get("url", "")
            title = source.get("title", "")
            snippet = source.get("snippet", "")
            
            # Basic credibility scoring based on domain
            credibility = self._score_domain_credibility(url)
            
            source_objects.append(SourceInfo(
                url=url,
                title=title or "Source",
                credibility=credibility,
                excerpt=snippet
            ))
        
        return source_objects

    def _score_domain_credibility(self, url: str) -> str:
        """
        Simple domain-based credibility scoring.
        """
        url_lower = url.lower()
        
        # High credibility domains
        high_credibility = [
            '.gov', '.edu', 'bbc.com', 'reuters.com', 'apnews.com',
            'nature.com', 'science.org', 'who.int', 'cdc.gov'
        ]
        
        # Low credibility indicators
        low_credibility = [
            'facebook.com', 'twitter.com', 'reddit.com', 
            'instagram.com', 'tiktok.com'
        ]
        
        for domain in high_credibility:
            if domain in url_lower:
                return "high"
        
        for domain in low_credibility:
            if domain in url_lower:
                return "low"
        
        return "medium"

    def _build_response_from_cache(self, cached_result: dict, intent: IntentType) -> QueryResponse:
        """Build QueryResponse from cached vector DB result."""
        metadata = cached_result.get("metadata", {})
        
        # Reconstruct sources from metadata
        sources = []
        for i in range(3):
            url = metadata.get(f"source_{i}_url", "")
            title = metadata.get(f"source_{i}_title", "")
            if url:
                sources.append(SourceInfo(
                    url=url,
                    title=title or "Cached Source",
                    credibility="medium"
                ))
        
        # Parse verdict
        verdict_str = metadata.get("verdict", "UNVERIFIED")
        try:
            verdict = VerdictType(verdict_str)
        except ValueError:
            verdict = VerdictType.UNVERIFIED
        
        return QueryResponse(
            intent=intent,
            verdict=verdict,
            confidence=metadata.get("confidence", 0.8),
            summary=metadata.get("summary", "Cached result"),
            sources=sources,
            search_used="vector_db"
        )

    def _generate_claim_id(self, query: str) -> str:
        """Generate unique ID for a claim based on query hash."""
        return hashlib.md5(query.lower().encode()).hexdigest()[:16]
    
    def _generate_conversational_response(self, query: str, context: str) -> str:
        """
        Generate a natural, conversational response for general queries.
        Unlike fact-checking, this should be ChatGPT-like and comprehensive.
        """
        if not context or len(context.strip()) == 0:
            context = "No search results available."
        
        formatted_prompt = CONVERSATIONAL_CHAT_PROMPT.format(query=query, context=context)
        
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=formatted_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PERSONA,
                    temperature=0.7  # Higher temperature for more natural conversation
                )
            )
            
            return response.text.strip()
            
        except Exception as e:
            print(f"ERROR in conversational response: {e}")
            # Fallback to context if generation fails
            return context[:1000] if context else "I apologize, but I encountered an error generating a response."
    
    def _check_for_duplicate(self, query: str) -> bool:
        """
        Check if query is a near-duplicate of an existing vector DB entry
        
        Returns True if duplicate found (similarity > VECTOR_DUPLICATE_THRESHOLD)
        """
        if not self.vector_service.is_enabled():
            return False
        
        try:
            # Query vector DB for similar items
            similar = self.vector_service.query_similar_claims(query, top_k=1)
            
            if similar and len(similar) > 0:
                top_match_score = similar[0]['score']
                
                # If above duplicate threshold, it's a duplicate
                if top_match_score >= Config.VECTOR_DUPLICATE_THRESHOLD:
                    print(f"🔍 Duplicate detected! Similarity: {top_match_score:.3f} (threshold: {Config.VECTOR_DUPLICATE_THRESHOLD})")
                    return True
            
            return False
        except Exception as e:
            print(f"⚠️  Error checking for duplicates: {e}")
            return False  # On error, assume not duplicate (store anyway)

    def _enhance_with_credibility(self, verdict_data: dict, sources_list: list) -> dict:
        """
        Enhance verdict data with credibility scores from actual sources
        
        Args:
            verdict_data: Verdict dict from parser
            sources_list: List of source dicts with URLs and titles
            
        Returns:
            Enhanced verdict_data with credibility scores added to evidence
        """
        try:
            evidence = verdict_data.get('evidence', {})
            
            # Rank all sources by credibility
            ranked_sources = CredibilityScorer.rank_evidence_by_credibility([
                {
                    'url': s.get('url', ''),
                    'title': s.get('title', ''),
                    'excerpt': s.get('snippet', '')
                }
                for s in sources_list
            ])
            
            # Map URLs to credibility scores
            url_to_credibility = {s['url']: s['credibility_score'] for s in ranked_sources}
            
            # Enhance evidence items with credibility scores
            for category in ['supporting', 'contradicting', 'neutral']:
                if category in evidence and isinstance(evidence[category], list):
                    enhanced_items = []
                    for item in evidence[category]:
                        if isinstance(item, dict):
                            # Add credibility score if we have it
                            url = item.get('url', '')
                            if url in url_to_credibility:
                                item['credibility_score'] = url_to_credibility[url]
                            elif 'credibility_score' not in item:
                                # Compute it if not present
                                item['credibility_score'] = CredibilityScorer.score_source(
                                    url, 
                                    item.get('title', ''),
                                    item.get('excerpt', '')
                                )
                            enhanced_items.append(item)
                    evidence[category] = enhanced_items
            
            verdict_data['evidence'] = evidence
            
            # Set primary source from highest credibility
            if ranked_sources:
                primary_url = ranked_sources[0]['url']
                if 'provenance' in verdict_data:
                    verdict_data['provenance']['primary_source'] = primary_url
            
            return verdict_data
            
        except Exception as e:
            print(f"⚠️  Error enhancing credibility: {e}")
            return verdict_data  # Return unchanged on error

    def _retry_verdict_parse(self, query: str, context: str, timestamp: str, error_msg: str) -> dict:
        """
        Retry verdict synthesis with a clarifying follow-up prompt
        
        Args:
            query: Original query
            context: Search context
            timestamp: UTC timestamp
            error_msg: Error message from first attempt
            
        Returns:
            Verdict dict (or fallback if retry also fails)
        """
        retry_prompt = f"""Your previous response could not be parsed. Error: {error_msg}

Please try again, following the format EXACTLY:

First, output ONLY the JSON object (no extra text):
{{
  "verdict": "...",
  "confidence": 0.X,
  ...
}}

Then add a blank line.

Then add the summary line:
Short summary: ...

Original query: {query}
Context: {context[:500]}
"""
        
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=retry_prompt,
                config=types.GenerateContentConfig(
                    temperature=0.1
                )
            )
            
            verdict_data = VerdictParser.parse(response.text.strip())
            verdict_data['timestamp'] = timestamp
            print("✅ Retry successful!")
            return verdict_data
            
        except Exception as e:
            print(f"❌ Retry also failed: {e}")
            return VerdictParser.create_fallback_verdict(
                query=query,
                context=context[:500],
                reason="Failed to parse structured response after retry"
            )
