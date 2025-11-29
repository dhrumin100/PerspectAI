"""
Agent 3: Planning Agent - Testing Page
"""

import streamlit as st
import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agents.agent_01_query_analyzer import QueryAnalyzerAgent
from agents.agent_02_source_finder import SourceFinderAgent
from agents.agent_03_planning_agent import PlanningAgent

st.set_page_config(page_title="Agent 3: Planning Agent", page_icon="🧠", layout="wide")

st.title("🧠 Agent 3: Planning Agent")
st.markdown("**Analyze initial results and generate research strategy**")

st.divider()

# Sidebar
with st.sidebar:
    st.markdown("### About Agent 3")
    st.info("""
    **Capabilities:**
    - Analyze search results
    - Identify information gaps
    - Generate research questions
    - Prioritize tasks
    
    **Input:** Search Results (from Agent 2)
    **Output:** Research Plan & Questions
    """)

# Main Content
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### 1️⃣ Input Claim")
    
    user_input = st.text_area(
        "Enter claim to plan for:",
        value="India will ban XYZ platform next week",
        height=100
    )
    
    if st.button("🧠 Generate Plan", type="primary", use_container_width=True):
        if user_input:
            try:
                with st.status("Running Pipeline...", expanded=True) as status:
                    # Step 1: Analyze
                    st.write("🔍 Agent 1: Analyzing claim...")
                    analyzer = QueryAnalyzerAgent()
                    structured_claim = analyzer.analyze(user_input)
                    
                    # Step 2: Find Sources
                    st.write("🌐 Agent 2: Finding initial sources...")
                    finder = SourceFinderAgent()
                    source_results = finder.find_sources(structured_claim)
                    st.write(f"✅ Found {source_results.total_found} sources")
                    
                    # Step 3: Plan
                    st.write("🧠 Agent 3: Creating research plan...")
                    planner = PlanningAgent()
                    plan = planner.create_plan(source_results)
                    
                    status.update(label="Planning Complete!", state="complete", expanded=False)
                
                # Store results
                st.session_state['plan_results'] = plan
                st.session_state['source_results_for_plan'] = source_results
                
            except Exception as e:
                st.error(f"Error: {str(e)}")

with col2:
    st.markdown("### 2️⃣ Research Plan")
    
    if 'plan_results' in st.session_state:
        plan = st.session_state['plan_results']
        
        # Gaps
        with st.expander("🕳️ Identified Gaps", expanded=True):
            for gap in plan.identified_gaps:
                st.markdown(f"- {gap}")
        
        # Questions
        st.markdown("#### 📋 Research Questions")
        
        # Sort by priority
        sorted_questions = sorted(plan.research_questions, key=lambda x: x.priority)
        
        for q in sorted_questions:
            priority_color = {1: "🔴", 2: "🟠", 3: "🟡"}.get(q.priority, "⚪")
            
            st.markdown(f"""
            <div style="padding: 10px; border-left: 4px solid #7000ff; background: #f8f9fa; margin-bottom: 10px; border-radius: 0 5px 5px 0;">
                <div style="font-weight: bold; font-size: 1.1em;">{priority_color} P{q.priority}: {q.question}</div>
                <div style="color: #666; font-size: 0.9em; margin-top: 5px;">Rationale: {q.rationale}</div>
            </div>
            """, unsafe_allow_html=True)
            
        # JSON Output
        with st.expander("📄 Raw JSON Output"):
            st.json(json.loads(plan.model_dump_json()))

    else:
        st.info("👈 Enter a claim and click 'Generate Plan'")
