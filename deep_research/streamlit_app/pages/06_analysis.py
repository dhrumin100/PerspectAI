"""
Agent 6: Analysis & Reasoning - Testing Page
"""

import streamlit as st
import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agents.agent_06_analysis_reasoning import AnalysisReasoningAgent
from models.schemas import AggregatedData, TimelineEvent, KnowledgeGraph, Verdict

st.set_page_config(page_title="Agent 6: Analysis", page_icon="⚖️", layout="wide")

st.title("⚖️ Agent 6: Analysis & Reasoning")
st.markdown("**Evaluate evidence and generate a verdict**")

st.divider()

# Sidebar
with st.sidebar:
    st.markdown("### About Agent 6")
    st.info("""
    **Capabilities:**
    - Detect Contradictions
    - Evaluate Consensus
    - Generate Verdict
    - Calculate Confidence
    
    **Input:** Knowledge Base (from Agent 5)
    **Output:** Verdict & Reasoning
    """)

# Main Content
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### 1️⃣ Input Data")
    
    claim_input = st.text_area("Claim to Verify:", value="India will ban XYZ platform next week")
    
    if st.button("⚖️ Analyze Claim", type="primary", use_container_width=True):
        try:
            with st.status("Analyzing...", expanded=True) as status:
                # Mock Data
                mock_data = AggregatedData(
                    unique_facts=[
                        "Government officials denied any ban plans.",
                        "No official notification has been released.",
                        "Social media rumors started on Twitter."
                    ],
                    timeline=[
                        TimelineEvent(date="2025-11-20", event="Rumor started", source="Twitter", importance=5),
                        TimelineEvent(date="2025-11-21", event="Ministry denial", source="PIB", importance=10)
                    ],
                    knowledge_graph=KnowledgeGraph(nodes=[], edges=[]),
                    credibility_map={"PIB": 1.0, "Twitter": 0.3}
                )
                
                agent = AnalysisReasoningAgent()
                result = agent.analyze_claim(claim_input, mock_data)
                
                status.update(label="Analysis Complete!", state="complete", expanded=False)
            
            st.session_state['analysis_output'] = result
            
        except Exception as e:
            st.error(f"Error: {str(e)}")

with col2:
    st.markdown("### 2️⃣ Verdict")
    
    if 'analysis_output' in st.session_state:
        res = st.session_state['analysis_output']
        
        # Verdict Display
        color_map = {
            Verdict.CONFIRMED_TRUE: "green",
            Verdict.LIKELY_TRUE: "lightgreen",
            Verdict.UNCERTAIN: "orange",
            Verdict.LIKELY_FALSE: "salmon",
            Verdict.CONFIRMED_FALSE: "red"
        }
        color = color_map.get(res.verdict, "grey")
        
        st.markdown(f"""
        <div style="text-align: center; padding: 20px; background-color: {color}; color: white; border-radius: 10px; margin-bottom: 20px;">
            <h2 style="margin:0;">{res.verdict.value.replace('_', ' ')}</h2>
            <p style="margin:0; font-size: 1.2em;">Confidence: {res.confidence * 100:.1f}%</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"**Reasoning:** {res.reasoning}")
        st.markdown(f"**Consensus:** {res.consensus_view}")
        
        # Evidence
        with st.expander("🔍 Evidence Breakdown", expanded=True):
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown("**✅ Supporting:**")
                for item in res.evidence.supporting:
                    st.markdown(f"- {item}")
            with col_b:
                st.markdown("**❌ Contradicting:**")
                for item in res.evidence.contradicting:
                    st.markdown(f"- {item}")
                    
        # Red Flags
        if res.red_flags:
            st.error(f"**🚩 Red Flags:** {', '.join(res.red_flags)}")
                
    else:
        st.info("👈 Click 'Analyze Claim'")
