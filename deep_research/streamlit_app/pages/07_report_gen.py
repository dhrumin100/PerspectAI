"""
Agent 7: Report Generator - Testing Page
"""

import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agents.agent_07_report_generator import ReportGeneratorAgent
from models.schemas import AnalysisOutput, AggregatedData, Verdict, Evidence, TimelineEvent, KnowledgeGraph

st.set_page_config(page_title="Agent 7: Report Generator", page_icon="📝", layout="wide")

st.title("📝 Agent 7: Report Generator")
st.markdown("**Generate comprehensive reports in Markdown and PDF**")

st.divider()

# Sidebar
with st.sidebar:
    st.markdown("### About Agent 7")
    st.info("""
    **Capabilities:**
    - Generate Narrative
    - Format Markdown
    - Export PDF
    
    **Input:** Analysis & Data
    **Output:** Report Files
    """)

# Main Content
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### 1️⃣ Input Analysis")
    
    if st.button("📝 Generate Report", type="primary", use_container_width=True):
        try:
            with st.status("Generating Report...", expanded=True) as status:
                # Mock Data
                mock_analysis = AnalysisOutput(
                    verdict=Verdict.LIKELY_FALSE,
                    confidence=0.85,
                    reasoning="Multiple official sources deny the claim.",
                    evidence=Evidence(
                        supporting=["One viral tweet"],
                        contradicting=["Ministry statement", "News report"]
                    ),
                    red_flags=["No official source"],
                    consensus_view="False"
                )
                
                mock_data = AggregatedData(
                    unique_facts=["Fact 1", "Fact 2"],
                    timeline=[
                        TimelineEvent(date="2025-11-20", event="Rumor started", source="Twitter", importance=5)
                    ],
                    knowledge_graph=KnowledgeGraph(nodes=[], edges=[]),
                    credibility_map={}
                )
                
                agent = ReportGeneratorAgent()
                report = agent.generate_report(
                    "India will ban XYZ platform",
                    mock_analysis,
                    mock_data
                )
                
                status.update(label="Report Generated!", state="complete", expanded=False)
            
            st.session_state['report_output'] = report
            
        except Exception as e:
            st.error(f"Error: {str(e)}")

with col2:
    st.markdown("### 2️⃣ Report Preview")
    
    if 'report_output' in st.session_state:
        report = st.session_state['report_output']
        
        st.markdown(f"# {report.title}")
        st.markdown(f"**Verdict:** {report.verdict.value}")
        
        st.markdown("### Executive Summary")
        st.write(report.executive_summary)
        
        st.markdown("### Key Findings")
        for f in report.key_findings:
            st.markdown(f"- {f}")
            
        st.divider()
        
        # Download Buttons
        st.download_button(
            label="📥 Download Markdown",
            data=report.model_dump_json(), # Placeholder for actual MD content
            file_name="report.md",
            mime="text/markdown"
        )
        
        st.info("PDF saved to `deep_research/reports/` folder")
                
    else:
        st.info("👈 Click 'Generate Report'")
