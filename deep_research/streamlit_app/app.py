"""
Streamlit Testing App for Deep Research System
Main dashboard for testing all 9 agents individually
"""

import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

st.set_page_config(
    page_title="Deep Research System - Testing Hub",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(135deg, #00f2ff 0%, #7000ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1rem;
    }
    .subtitle {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .agent-card {
        padding: 1.5rem;
        border-radius: 10px;
        background: #f0f2f6;
        margin: 1rem 0;
       border-left: 4px solid #00f2ff;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">🔬 Deep Research System</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">9-Agent Fact-Checking Pipeline - Individual Testing Interface</p>', unsafe_allow_html=True)

st.divider()

# Introduction
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("""
    ## Welcome to the Deep Research Testing Hub
    
    This Streamlit app allows you to **test each of the 9 agents individually** before integrating them
    into the full pipeline with CrewAI orchestration.
    
    ### 🤖 The 9 Agents:
    
    1. **Query Analyzer** - Extracts and structures user claims
    2. **Source Finder** - Discovers relevant web sources
    3. **Planning Agent** - Generates research strategy
    4. **Parallel Research** - Deep multi-threaded research
    5. **Data Aggregator** - Builds knowledge graph
    6. **Analysis & Reasoning** - Generates verdicts
    7. **Report Generator** - Creates comprehensive reports
    8. **Infographic Generator** - Visualizes results
    9. **Chat Interface** - Interactive Q&A (RAG)
    
    ### 📋 How to Use:
    
    1. Select an agent from the **sidebar** navigation
    2. Provide the required input for that agent
    3. Click "Run Agent" to see the output
    4. Review results and test different inputs
    5. Once satisfied, move to the next agent
    
    ### 🔄 Testing Workflow:
    
    - Test each agent **independently** first
    - Verify outputs match expected formats
    - Test edge cases and error handling
    - Once all agents work individually, test the **full pipeline**
    """)

with col2:
    st.markdown("### 🎯 System Status")
    
    # Try to import and check components
    status = {}
    
    try:
        from config.settings import Settings
        status["Configuration"] = "✅ Loaded"
    except:
        status["Configuration"] = "❌ Error"
    
    try:
        from agents.agent_01_query_analyzer import QueryAnalyzerAgent
        status["Agent 1"] = "✅ Ready"
    except:
        status["Agent 1"] = "⚠️ Not Implemented"
    
    status["Agent 2-9"] = "🔨 In Development"
    status["CrewAI Integration"] = "⏳ Pending"
    
    for component, state in status.items():
        st.markdown(f"**{component}:** {state}")

st.divider()

# Quick Start
st.markdown("### 🚀 Quick Start")
col1, col2, col3 = st.columns(3)

with col1:
    st.info("""
    **Step 1: Test Individual Agents**
    
    Navigate to each agent page from the sidebar and test with sample inputs.
    """)

with col2:
    st.info("""
    **Step 2: Verify Outputs**
    
    Ensure each agent produces the expected structured output format.
    """)

with col3:
    st.info("""
    **Step 3: Full Pipeline**
    
    Once all agents work, test the complete orchestrated workflow.
    """)

st.divider()

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p><strong>PerspectAI Deep Research System</strong> | Built with CrewAI, LlamaIndex, LangChain & Streamlit</p>
    <p>For integration questions, check the main documentation</p>
</div>
""", unsafe_allow_html=True)
