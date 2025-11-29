"""
Agent 4: Parallel Research Agent
Conducts deep research by scraping and analyzing web content
"""

import asyncio
import aiohttp
from bs4 import BeautifulSoup
from typing import List, Dict
from loguru import logger
import google.generativeai as genai
import json

from config.settings import Settings
from config.prompts import RESEARCH_AGENT_PROMPT
from models.schemas import ResearchQuestion, ParallelResearchOutput, ResearchFinding, SearchResult

# Configure Gemini
genai.configure(api_key=Settings.GOOGLE_API_KEY)

class ParallelResearchAgent:
    """
    Agent 4: Deep Research & Content Extraction
    
    Capabilities:
    - Async web scraping
    - Content extraction and cleaning
    - Relevance scoring
    - Summarization
    """
    
    def __init__(self):
        self.model = genai.GenerativeModel(
            model_name=Settings.DEFAULT_MODEL,
            generation_config={
                "temperature": Settings.TEMPERATURE,
                "max_output_tokens": Settings.MAX_TOKENS,
            }
        )
        logger.info("ParallelResearchAgent initialized")

    async def research_questions(self, questions: List[ResearchQuestion], sources: List[SearchResult]) -> List[ParallelResearchOutput]:
        """
        Execute research for multiple questions in parallel
        
        Args:
            questions: List of research questions from Agent 3
            sources: List of sources from Agent 2
            
        Returns:
            List of research outputs
        """
        logger.info(f"Starting research for {len(questions)} questions...")
        
        tasks = []
        for q in questions:
            tasks.append(self._research_single_question(q, sources))
            
        results = await asyncio.gather(*tasks)
        return results

    async def _research_single_question(self, question: ResearchQuestion, sources: List[SearchResult]) -> ParallelResearchOutput:
        """Research a single question"""
        logger.info(f"Researching: {question.question}")
        
        # 1. Select relevant sources for this question
        # In a real system, we might search again. Here we filter existing sources.
        # For simplicity, we'll use the top 3 sources for now.
        target_sources = sources[:3]
        
        findings = []
        
        # 2. Scrape and Extract
        async with aiohttp.ClientSession() as session:
            scrape_tasks = [self._scrape_url(session, s.url) for s in target_sources]
            scraped_contents = await asyncio.gather(*scrape_tasks)
            
            for source, content in zip(target_sources, scraped_contents):
                if content:
                    # 3. Analyze Content with LLM
                    finding = await self._analyze_content(question.question, content, source)
                    if finding:
                        findings.append(finding)
        
        # 4. Summarize Findings
        summary = await self._summarize_findings(question.question, findings)
        
        return ParallelResearchOutput(
            question=question.question,
            findings=findings,
            summary=summary,
            confidence=0.85 if findings else 0.0
        )

    async def _scrape_url(self, session: aiohttp.ClientSession, url: str) -> str:
        """Scrape text content from URL"""
        try:
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Remove script and style elements
                    for script in soup(["script", "style"]):
                        script.decompose()
                        
                    text = soup.get_text()
                    
                    # Clean text
                    lines = (line.strip() for line in text.splitlines())
                    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                    text = '\n'.join(chunk for chunk in chunks if chunk)
                    
                    return text[:5000] # Limit content length
        except Exception as e:
            logger.warning(f"Failed to scrape {url}: {e}")
            return ""
        return ""

    async def _analyze_content(self, question: str, content: str, source: SearchResult) -> ResearchFinding:
        """Extract relevant findings using LLM"""
        try:
            prompt = f"""
            Question: {question}
            
            Source Content:
            {content[:2000]}...
            
            Extract a relevant finding that answers the question.
            Return JSON: {{ "excerpt": "...", "relevance": 0.9 }}
            If no relevant info, return null.
            """
            
            response = await asyncio.to_thread(self.model.generate_content, prompt)
            text = response.text.strip()
            
            if "null" in text.lower():
                return None
                
            # Extract JSON
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
                
            data = json.loads(text)
            
            return ResearchFinding(
                source_url=source.url,
                excerpt=data.get("excerpt", "")[:200],
                relevance=data.get("relevance", 0.5),
                credibility_score=0.8 # Placeholder
            )
            
        except Exception as e:
            logger.error(f"Error analyzing content: {e}")
            return None

    async def _summarize_findings(self, question: str, findings: List[ResearchFinding]) -> str:
        """Summarize all findings for a question"""
        if not findings:
            return "No relevant information found."
            
        context = "\n".join([f"- {f.excerpt}" for f in findings])
        
        try:
            prompt = f"""
            Question: {question}
            Findings:
            {context}
            
            Summarize the answer based on these findings.
            """
            response = await asyncio.to_thread(self.model.generate_content, prompt)
            return response.text.strip()
        except:
            return "Error generating summary."

if __name__ == "__main__":
    # Test
    pass
