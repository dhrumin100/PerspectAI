"""
Agent 2: Source Finder - Testing Page
"""

import streamlit as st
import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agents.agent_01_query_analyzer import QueryAnalyzerAgent
from agents.agent_02_source_finder import SourceFinderAgent
from models.schemas import StructuredClaim

st.set_page_config(page_title="Agent 2: Source Finder", page_icon="🌐", layout="wide")

st.title("🌐 Agent 2: Source Finder")
st.markdown("**Discover relevant web sources and news articles**")

st.divider()

# Sidebar
with st.sidebar:
    st.markdown("### About Agent 2")
    st.info("""
    **Capabilities:**
    - Generate search queries
    - Search Web (SerpAPI)
    - Search News (NewsAPI)
    - Filter & Rank results
    
    **Input:** Structured Claim (from Agent 1)
    **Output:** List of relevant sources
    """)
    
    # Check API Keys
    from config.settings import Settings
    st.markdown("### API Status")
    if Settings.SERPAPI_KEY:
        st.success("✅ SerpAPI Configured")
    else:
        st.warning("⚠️ SerpAPI Missing (Using Mock)")
        
    if Settings.NEWS_API_KEY:
        st.success("✅ NewsAPI Configured")
    else:
        st.warning("⚠️ NewsAPI Missing")

# Main Content
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### 1️⃣ Input Claim")
    
    user_input = st.text_area(
        "Enter claim to research:",
        value="India will ban XYZ platform next week",
        height=100
    )
    
    if st.button("🚀 Find Sources", type="primary", use_container_width=True):
        if user_input:
            try:
                with st.status("Running Agents...", expanded=True) as status:
                    # Step 1: Analyze (Agent 1)
                    st.write("🔍 Agent 1: Analyzing claim...")
                    analyzer = QueryAnalyzerAgent()
                    structured_claim = analyzer.analyze(user_input)
                    st.write("✅ Claim structured")
                    
                    # Step 2: Find Sources (Agent 2)
                    st.write("🌐 Agent 2: Searching web...")
                    finder = SourceFinderAgent()
                    result = finder.find_sources(structured_claim)
                    st.write(f"✅ Found {result.total_found} sources")
                    
                    status.update(label="Search Complete!", state="complete", expanded=False)
                
                # Store results
                st.session_state['source_results'] = result
                st.session_state['structured_claim'] = structured_claim
                
            except Exception as e:
                st.error(f"Error: {str(e)}")

with col2:
    st.markdown("### 2️⃣ Search Results")
    
    if 'source_results' in st.session_state:
        result = st.session_state['source_results']
        
        # Display Queries
        with st.expander("🔎 Generated Search Queries", expanded=False):
            for q in result.search_queries:
                st.markdown(f"- `{q}`")
        
        # Display Sources
        st.markdown(f"**Found {result.total_found} Sources:**")
        
        for source in result.sources:
            with st.container():
                st.markdown(f"""
                <div style="padding: 10px; border: 1px solid #ddd; border-radius: 5px; margin-bottom: 10px;">
                    <a href="{source.url}" target="_blank" style="font-weight: bold; font-size: 1.1em; text-decoration: none;">{source.title}</a>
                    <br>
                    <span style="color: #666; font-size: 0.9em;">{source.source_type.value.upper()} • Score: {source.relevance_score}</span>
                    <p style="margin-top: 5px; font-size: 0.95em;">{source.snippet}</p>
                </div>
                """, unsafe_allow_html=True)
                
        # JSON Output
        with st.expander("📄 Raw JSON Output"):
            st.json(json.loads(result.model_dump_json()))

    else:
        st.info("👈 Enter a claim and click 'Find Sources'")
