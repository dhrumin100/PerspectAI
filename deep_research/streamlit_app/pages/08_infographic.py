"""
Agent 8: Infographic Generator - Testing Page
"""

import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agents.agent_08_infographic_generator import InfographicGeneratorAgent
from models.schemas import AnalysisOutput, AggregatedData, Verdict, Evidence, TimelineEvent, KnowledgeGraph

st.set_page_config(page_title="Agent 8: Infographics", page_icon="🎨", layout="wide")

st.title("🎨 Agent 8: Infographic Generator")
st.markdown("**Visualize analysis results with interactive charts**")

st.divider()

# Sidebar
with st.sidebar:
    st.markdown("### About Agent 8")
    st.info("""
    **Capabilities:**
    - Truth Meter
    - Timeline Chart
    - Credibility Distribution
    
    **Input:** Analysis & Data
    **Output:** Plotly Charts
    """)

# Main Content
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### 1️⃣ Input Data")
    
    if st.button("🎨 Generate Visuals", type="primary", use_container_width=True):
        try:
            with st.status("Generating Charts...", expanded=True) as status:
                # Mock Data
                mock_analysis = AnalysisOutput(
                    verdict=Verdict.LIKELY_FALSE,
                    confidence=0.85,
                    reasoning="Reasoning...",
                    evidence=Evidence(supporting=[], contradicting=[]),
                    red_flags=[],
                    consensus_view="False"
                )
                
                mock_data = AggregatedData(
                    unique_facts=[],
                    timeline=[
                        TimelineEvent(date="2025-11-20", event="Rumor started", source="Twitter", importance=5),
                        TimelineEvent(date="2025-11-21", event="Denial issued", source="Govt", importance=10),
                        TimelineEvent(date="2025-11-22", event="News coverage", source="BBC", importance=8)
                    ],
                    knowledge_graph=KnowledgeGraph(nodes=[], edges=[]),
                    credibility_map={"Twitter": 0.3, "Govt": 1.0, "BBC": 0.9}
                )
                
                agent = InfographicGeneratorAgent()
                charts = agent.create_visualizations(mock_analysis, mock_data)
                
                status.update(label="Visuals Ready!", state="complete", expanded=False)
            
            st.session_state['charts'] = charts
            
        except Exception as e:
            st.error(f"Error: {str(e)}")

with col2:
    st.markdown("### 2️⃣ Visualizations")
    
    if 'charts' in st.session_state:
        charts = st.session_state['charts']
        
        st.markdown("#### Truth Meter")
        st.plotly_chart(charts["truth_meter"], use_container_width=True)
        
        st.markdown("#### Timeline")
        st.plotly_chart(charts["timeline_chart"], use_container_width=True)
        
        st.markdown("#### Credibility Scores")
        st.plotly_chart(charts["credibility_chart"], use_container_width=True)
                
    else:
        st.info("👈 Click 'Generate Visuals'")
