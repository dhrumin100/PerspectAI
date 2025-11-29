"""
Agent 2: Source Finder
Discovers relevant web sources using multiple search APIs
"""

import json
import os
from typing import List, Dict, Any
from loguru import logger
import google.generativeai as genai
from serpapi import GoogleSearch
from newsapi import NewsApiClient

from config.settings import Settings
from config.prompts import SOURCE_FINDER_PROMPT
from models.schemas import StructuredClaim, SourceFinderOutput, SearchResult, SourceType

# Configure Gemini
genai.configure(api_key=Settings.GOOGLE_API_KEY)

class SourceFinderAgent:
    """
    Agent 2: Finds relevant sources from web and news APIs
    
    Capabilities:
    - Generate targeted search queries
    - Search Google via SerpAPI
    - Search News via NewsAPI
    - Filter and rank results
    """
    
    def __init__(self):
        self.model = genai.GenerativeModel(
            model_name=Settings.DEFAULT_MODEL,
            generation_config={
                "temperature": Settings.TEMPERATURE,
                "max_output_tokens": Settings.MAX_TOKENS,
            }
        )
        
        # Initialize Search APIs
        self.serpapi_key = Settings.SERPAPI_KEY
        self.newsapi_key = Settings.NEWS_API_KEY
        
        if self.newsapi_key:
            self.newsapi = NewsApiClient(api_key=self.newsapi_key)
        else:
            self.newsapi = None
            logger.warning("NewsAPI key not found. News search will be disabled.")
            
        logger.info("SourceFinderAgent initialized")

    def find_sources(self, structured_claim: StructuredClaim) -> SourceFinderOutput:
        """
        Find sources for a structured claim
        
        Args:
            structured_claim: Structured output from Agent 1
            
        Returns:
            SourceFinderOutput with search queries and results
        """
        logger.info(f"Finding sources for claim: {structured_claim.original_claim[:50]}...")
        
        # 1. Generate Search Queries
        queries = self._generate_queries(structured_claim)
        
        # 2. Execute Searches
        all_results = []
        
        # Web Search (SerpAPI)
        if self.serpapi_key:
            web_results = self._search_web(queries[:3]) # Use top 3 queries
            all_results.extend(web_results)
        else:
            logger.warning("SerpAPI key missing. Skipping web search.")
            # Mock results for testing if no key
            if not self.serpapi_key and not self.newsapi_key:
                all_results.extend(self._get_mock_results(queries[0]))
        
        # News Search (NewsAPI)
        if self.newsapi:
            news_results = self._search_news(queries[0]) # Use primary query
            all_results.extend(news_results)
            
        # 3. Deduplicate and Rank
        unique_results = self._deduplicate_results(all_results)
        
        return SourceFinderOutput(
            search_queries=queries,
            sources=unique_results,
            total_found=len(unique_results)
        )
    
    def _generate_queries(self, claim: StructuredClaim) -> List[str]:
        """Generate search queries using LLM"""
        try:
            prompt = SOURCE_FINDER_PROMPT.format(
                structured_claim=claim.model_dump_json(indent=2)
            )
            
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            
            # Extract JSON
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
                
            queries = json.loads(text)
            
            # Handle different return formats
            cleaned_queries = []
            
            # Case 1: {"queries": [...]}
            if isinstance(queries, dict) and "queries" in queries:
                raw_list = queries["queries"]
            # Case 2: List of items
            elif isinstance(queries, list):
                raw_list = queries
            else:
                raw_list = [claim.original_claim]
                
            # Extract strings from list
            for item in raw_list:
                if isinstance(item, str):
                    cleaned_queries.append(item)
                elif isinstance(item, dict) and "query" in item:
                    cleaned_queries.append(item["query"])
            
            # Fallback if empty
            if not cleaned_queries:
                return [claim.original_claim]
                
            return cleaned_queries
                
        except Exception as e:
            logger.error(f"Error generating queries: {e}")
            return [claim.original_claim]

    def _search_web(self, queries: List[str]) -> List[SearchResult]:
        """Search Google using SerpAPI"""
        results = []
        for query in queries:
            try:
                logger.info(f"Searching web for: {query}")
                search = GoogleSearch({
                    "q": query,
                    "api_key": self.serpapi_key,
                    "num": 5
                })
                data = search.get_dict()
                
                if "organic_results" in data:
                    for item in data["organic_results"]:
                        results.append(SearchResult(
                            url=item.get("link"),
                            title=item.get("title"),
                            snippet=item.get("snippet"),
                            source_type=SourceType.UNKNOWN,
                            relevance_score=0.8 # Placeholder score
                        ))
            except Exception as e:
                logger.error(f"SerpAPI error for '{query}': {e}")
        return results

    def _search_news(self, query: str) -> List[SearchResult]:
        """Search news using NewsAPI"""
        results = []
        
        # Skip if NewsAPI is not configured
        if not self.newsapi:
            return results
            
        try:
            logger.info(f"Searching news for: {query}")
            data = self.newsapi.get_everything(
                q=query,
                language='en',
                sort_by='relevancy',
                page_size=5
            )
            
            if "articles" in data:
                for item in data["articles"]:
                    results.append(SearchResult(
                        url=item.get("url"),
                        title=item.get("title"),
                        snippet=item.get("description"),
                        date=item.get("publishedAt"),
                        source_type=SourceType.NEWS,
                        relevance_score=0.9
                    ))
        except Exception as e:
            # Only log error if NewsAPI key was configured but failed
            if self.newsapi_key:
                logger.error(f"NewsAPI error: {e}")
        return results

    def _deduplicate_results(self, results: List[SearchResult]) -> List[SearchResult]:
        """Remove duplicate URLs"""
        seen_urls = set()
        unique = []
        for r in results:
            if r.url not in seen_urls:
                seen_urls.add(r.url)
                unique.append(r)
        return unique

    def _get_mock_results(self, query: str) -> List[SearchResult]:
        """Return mock results for testing without API keys"""
        return [
            SearchResult(
                url="https://example.com/article1",
                title=f"Analysis of {query}",
                snippet="This is a mock search result for testing purposes.",
                source_type=SourceType.NEWS,
                relevance_score=0.95
            ),
            SearchResult(
                url="https://example.org/fact-check",
                title="Fact Check: Verified Information",
                snippet="Official sources confirm that the claim is...",
                source_type=SourceType.FACT_CHECKER,
                relevance_score=0.90
            )
        ]

if __name__ == "__main__":
    # Test
    agent = SourceFinderAgent()
    claim = StructuredClaim(
        original_claim="Test claim",
        entities=None, # Mock
        claim_type="factual_claim",
        urgency="low"
    )
    # This will fail without proper StructuredClaim, but good for syntax check
