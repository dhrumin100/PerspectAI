"""
Agent 9: Chat Interface - Testing Page
"""

import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agents.agent_09_chat_interface import ChatInterfaceAgent
from models.schemas import Report, Verdict

st.set_page_config(page_title="Agent 9: Chat Interface", page_icon="💬", layout="wide")

st.title("💬 Agent 9: Chat Interface")
st.markdown("**Interactive Q&A with the Research Report**")

st.divider()

# Sidebar
with st.sidebar:
    st.markdown("### About Agent 9")
    st.info("""
    **Capabilities:**
    - RAG (Retrieval Augmented Generation)
    - Context-aware answers
    - Source citation
    
    **Input:** User Question
    **Output:** AI Answer
    """)

# Main Content
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### 1️⃣ Load Report")
    
    if st.button("📚 Load Mock Report", type="primary", use_container_width=True):
        with st.spinner("Indexing Report..."):
            # Mock Report
            mock_report = Report(
                title="Investigation into XYZ Ban",
                executive_summary="The claim that India will ban XYZ platform is likely false. No official sources confirm this.",
                claim="India will ban XYZ platform",
                verdict=Verdict.LIKELY_FALSE,
                confidence=0.85,
                key_findings=["No Ministry notification found", "Rumor originated on Twitter"],
                evidence_analysis="Detailed analysis...",
                timeline=[],
                source_evaluation="Sources checked...",
                conclusion="The claim is unsubstantiated.",
                sources_bibliography=[]
            )
            
            agent = ChatInterfaceAgent()
            agent.load_report(mock_report)
            
            st.session_state['chat_agent'] = agent
            st.success("Report Loaded & Indexed!")

with col2:
    st.markdown("### 2️⃣ Chat")
    
    if 'chat_agent' in st.session_state:
        agent = st.session_state['chat_agent']
        
        # Chat History
        if "messages" not in st.session_state:
            st.session_state.messages = []

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # User Input
        if prompt := st.chat_input("Ask about the report..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                response = agent.chat(prompt)
                st.markdown(response.answer)
                
                if response.sources:
                    st.caption(f"Sources: {', '.join(set(response.sources))}")
            
            st.session_state.messages.append({"role": "assistant", "content": response.answer})
            
    else:
        st.info("👈 Click 'Load Mock Report' first")
