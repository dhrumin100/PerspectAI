"""
Credibility scoring system for source evaluation
"""
from urllib.parse import urlparse
from typing import List, Dict
import re


class CredibilityScorer:
    """Compute source credibility scores based on domain reputation and content quality"""
    
    # High credibility domains with their base scores
    HIGH_CREDIBILITY_DOMAINS = {
        '.gov': 0.95,
        '.edu': 0.90,
        'who.int': 0.95,
        'cdc.gov': 0.95,
        'nih.gov': 0.95,
        'nature.com': 0.90,
        'science.org': 0.90,
        'sciencedirect.com': 0.85,
        'reuters.com': 0.85,
        'apnews.com': 0.85,
        'bbc.com': 0.80,
        'theguardian.com': 0.80,
        'nytimes.com': 0.80,
        'washingtonpost.com': 0.80,
        'npr.org': 0.80,
    }
    
    # Low credibility domains
    LOW_CREDIBILITY_DOMAINS = {
        'facebook.com': 0.30,
        'twitter.com': 0.35,
        'reddit.com': 0.40,
        'medium.com': 0.50,
        'wordpress.com': 0.45,
        'blogspot.com': 0.40,
        'tumblr.com': 0.35,
    }
    
    @classmethod
    def score_source(cls, url: str, title: str = "", excerpt: str = "") -> float:
        """
        Compute 0-1 credibility score for a source
        
        Scoring factors:
        - Domain reputation (70%)
        - Organization indicators (20%)  
        - Content quality indicators (10%)
        
        Args:
            url: Source URL
            title: Source title (optional)
            excerpt: Source excerpt (optional)
            
        Returns:
            float: Credibility score between 0.0 and 1.0
        """
        try:
            domain = urlparse(url).netloc.lower()
        except:
            return 0.50  # Default for malformed URLs
        
        # Check high credibility domains
        for pattern, score in cls.HIGH_CREDIBILITY_DOMAINS.items():
            if pattern in domain:
                return score
        
        # Check low credibility domains
        for pattern, score in cls.LOW_CREDIBILITY_DOMAINS.items():
            if pattern in domain:
                return score
        
        # Compute heuristic score for unknown sources
        base_score = 0.60  # Default for unknown sources
        
        # +15% for clear organization indicators
        org_keywords = ['university', 'institute', 'foundation', 'organization', 'association']
        if any(keyword in domain for keyword in org_keywords):
            base_score += 0.15
        
        # +10% for established news outlets
        news_keywords = ['news', 'times', 'post', 'journal', 'telegraph', 'herald']
        if any(keyword in domain for keyword in news_keywords):
            base_score += 0.10
        
        # -10% for personal blogs
        blog_keywords = ['blog', 'personal', 'diary']
        if any(keyword in domain for keyword in blog_keywords):
            base_score -= 0.10
        
        # -5% for overly commercial sites
        if any(keyword in domain for keyword in ['shop', 'store', 'buy', 'sale']):
            base_score -= 0.05
        
        return min(max(base_score, 0.0), 1.0)
    
    @classmethod
    def rank_evidence_by_credibility(cls, evidence_items: List[Dict]) -> List[Dict]:
        """
        Rank evidence items by credibility score
        
        Args:
            evidence_items: List of dicts with 'url', 'title', 'excerpt'
            
        Returns:
            Sorted list with credibility_score added to each item
        """
        scored_items = []
        
        for item in evidence_items:
            # Compute credibility score
            cred_score = cls.score_source(
                url=item.get('url', ''),
                title=item.get('title', ''),
                excerpt=item.get('excerpt', '')
            )
            
            # Add score to item
            item['credibility_score'] = round(cred_score, 2)
            scored_items.append(item)
        
        # Sort by credibility (descending)
        return sorted(scored_items, key=lambda x: x['credibility_score'], reverse=True)
    
    @classmethod
    def get_primary_source(cls, sources: List[Dict]) -> str:
        """
        Get the most credible source URL from a list
        
        Args:
            sources: List of source dicts with 'url' field
            
        Returns:
            URL of the most credible source, or empty string if no sources
        """
        if not sources:
            return ""
        
        ranked = cls.rank_evidence_by_credibility(sources)
        return ranked[0].get('url', '') if ranked else ""
