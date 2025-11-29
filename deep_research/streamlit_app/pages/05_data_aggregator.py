"""
Agent 5: Data Aggregator - Testing Page
"""

import streamlit as st
import sys
import json
import networkx as nx
import matplotlib.pyplot as plt
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agents.agent_05_data_aggregator import DataAggregatorAgent
from models.schemas import ParallelResearchOutput, ResearchFinding

st.set_page_config(page_title="Agent 5: Data Aggregator", page_icon="🔗", layout="wide")

st.title("🔗 Agent 5: Data Aggregator")
st.markdown("**Synthesize findings into Knowledge Graph & Timeline**")

st.divider()

# Sidebar
with st.sidebar:
    st.markdown("### About Agent 5")
    st.info("""
    **Capabilities:**
    - Deduplicate Facts
    - Build Timeline
    - Construct Knowledge Graph
    - Score Credibility
    
    **Input:** Research Findings (from Agent 4)
    **Output:** Knowledge Base
    """)

# Main Content
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### 1️⃣ Input Findings")
    
    if st.button("🔗 Run Aggregation", type="primary", use_container_width=True):
        try:
            with st.status("Aggregating...", expanded=True) as status:
                # Mock Data
                mock_findings = [
                    ParallelResearchOutput(
                        question="What happened?",
                        findings=[
                            ResearchFinding(
                                source_url="example.com",
                                excerpt="The event occurred on 2025-11-20.",
                                relevance=0.9,
                                credibility_score=0.9
                            )
                        ],
                        summary="Event details...",
                        confidence=0.9
                    )
                ]
                
                agent = DataAggregatorAgent()
                result = agent.aggregate_data(mock_findings)
                
                status.update(label="Aggregation Complete!", state="complete", expanded=False)
            
            st.session_state['agg_results'] = result
            
        except Exception as e:
            st.error(f"Error: {str(e)}")

with col2:
    st.markdown("### 2️⃣ Knowledge Base")
    
    if 'agg_results' in st.session_state:
        res = st.session_state['agg_results']
        
        # Timeline
        st.markdown("#### 📅 Timeline")
        for event in res.timeline:
            st.info(f"**{event.date}**: {event.event}")
            
        # Knowledge Graph
        st.markdown("#### 🕸️ Knowledge Graph")
        
        if res.knowledge_graph.nodes:
            # Simple visualization
            G = nx.Graph()
            for node in res.knowledge_graph.nodes:
                G.add_node(node['id'], label=node.get('label', ''))
            for edge in res.knowledge_graph.edges:
                G.add_edge(edge['source'], edge['target'], label=edge.get('relation', ''))
            
            fig, ax = plt.subplots()
            pos = nx.spring_layout(G)
            nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=1500, font_size=8)
            st.pyplot(fig)
            
        # Facts
        with st.expander("📝 Unique Facts"):
            for fact in res.unique_facts:
                st.markdown(f"- {fact}")
                
    else:
        st.info("👈 Click 'Run Aggregation'")
