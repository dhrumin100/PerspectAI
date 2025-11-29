"""
Agent 4: Parallel Research - Testing Page
"""

import streamlit as st
import sys
import asyncio
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agents.agent_04_parallel_research import ParallelResearchAgent
from models.schemas import ResearchQuestion, SearchResult, SourceType

st.set_page_config(page_title="Agent 4: Parallel Research", page_icon="⚡", layout="wide")

st.title("⚡ Agent 4: Parallel Research")
st.markdown("**Deep web scraping and content extraction**")

st.divider()

# Sidebar
with st.sidebar:
    st.markdown("### About Agent 4")
    st.info("""
    **Capabilities:**
    - Async Web Scraping
    - Content Extraction
    - Relevance Scoring
    - Summarization
    
    **Input:** Research Questions & Sources
    **Output:** Detailed Findings
    """)

# Main Content
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### 1️⃣ Input Data")
    
    # Mock Data for Testing
    st.markdown("#### Test Configuration")
    
    question_input = st.text_input(
        "Research Question:",
        value="What are the details of the XYZ platform ban?"
    )
    
    url_input = st.text_input(
        "Source URL to Scrape:",
        value="https://example.com"
    )
    
    if st.button("⚡ Run Research", type="primary", use_container_width=True):
        if question_input and url_input:
            try:
                with st.status("Researching...", expanded=True) as status:
                    # Create Mock Objects
                    questions = [ResearchQuestion(
                        question=question_input,
                        priority=1,
                        rationale="Test"
                    )]
                    
                    sources = [SearchResult(
                        url=url_input,
                        title="Test Source",
                        source_type=SourceType.NEWS,
                        relevance_score=0.9
                    )]
                    
                    # Run Agent
                    st.write("🕷️ Scraping and analyzing...")
                    agent = ParallelResearchAgent()
                    
                    # Run async function in sync context
                    results = asyncio.run(agent.research_questions(questions, sources))
                    
                    status.update(label="Research Complete!", state="complete", expanded=False)
                
                st.session_state['research_results'] = results
                
            except Exception as e:
                st.error(f"Error: {str(e)}")

with col2:
    st.markdown("### 2️⃣ Findings")
    
    if 'research_results' in st.session_state:
        results = st.session_state['research_results']
        
        for res in results:
            st.success(f"**Question:** {res.question}")
            st.markdown(f"**Summary:** {res.summary}")
            
            st.markdown("#### Evidence Found:")
            for finding in res.findings:
                st.info(f"""
                **Source:** {finding.source_url}  
                **Excerpt:** "{finding.excerpt}"  
                **Relevance:** {finding.relevance}
                """)
    else:
        st.info("👈 Enter details and click 'Run Research'")
