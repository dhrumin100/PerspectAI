"""
Agent 1: Query Analyzer - Testing Page
"""

import streamlit as st
import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agents.agent_01_query_analyzer import QueryAnalyzerAgent
from models.schemas import StructuredClaim

st.set_page_config(page_title="Agent 1: Query Analyzer", page_icon="🔍", layout="wide")

st.title("🔍 Agent 1: Query Analyzer")
st.markdown("**Extract and structure user claims for fact-checking**")

st.divider()

# Sidebar Info
with st.sidebar:
    st.markdown("### About Agent 1")
    st.info("""
    **Capabilities:**
    - Parse text input
    - Extract named entities
    - Identify claim type
    - Assess urgency level
    
    **Output:**
    Structured JSON with entities and metadata
    """)
    
    st.markdown("### Test Cases")
    test_claims = {
        "Policy": "India will ban XYZ platform next week",
        "Factual": "The Earth is flat",
        "Prediction": "Bitcoin will reach $100k by 2026",
        "Mixed": "President announced new policy yesterday that will affect millions"
    }
    
    selected_test = st.selectbox("Load test claim:", ["Custom"] + list(test_claims.keys()))

# Main content
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### 📝 Input")
    
    # Input text area
    if selected_test != "Custom":
        default_text = test_claims[selected_test]
    else:
        default_text = ""
    
    user_input = st.text_area(
        "Enter claim to analyze:",
        value=default_text,
        height=150,
        placeholder="Enter a claim, statement, or question to fact-check..."
    )
    
    # Run button
    if st.button("🔍 Analyze Claim", type="primary", use_container_width=True):
        if user_input.strip():
            with st.spinner("Analyzing claim..."):
                try:
                    # Initialize agent
                    agent = QueryAnalyzerAgent()
                    
                    # Analyze
                    result = agent.analyze(user_input)
                    
                    # Store in session state
                    st.session_state['analysis_result'] = result
                    st.session_state['analysis_input'] = user_input
                    
                    st.success("✅ Analysis complete!")
                    
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
        else:
            st.warning("⚠️ Please enter a claim to analyze")

with col2:
    st.markdown("### 📊 Output")
    
    if 'analysis_result' in st.session_state:
        result: StructuredClaim = st.session_state['analysis_result']
        
        # Display structured output
        st.json(json.loads(result.model_dump_json()))
        
        st.divider()
        
        # Formatted display
        st.markdown("#### Structured Breakdown")
        
        # Claim Type
        st.metric("Claim Type", result.claim_type.value.replace('_', ' ').title())
        st.metric("Urgency Level", result.urgency.value.upper())
        
        # Entities
        st.markdown("##### Extracted Entities")
        
        entities_data = {
            "👥 Actors": result.entities.actors,
            "⚡ Actions": result.entities.actions,
            "📦 Objects": result.entities.objects,
            "📅 Temporal": result.entities.temporal,
            "🌍 Geographic": result.entities.geographic
        }
        
        for entity_type, values in entities_data.items():
            if values:
                st.markdown(f"**{entity_type}:** {', '.join(values)}")
            else:
                st.markdown(f"**{entity_type}:** _(none detected)_")
        
        # Download button
        st.download_button(
            label="📥 Download JSON",
            data=result.model_dump_json(indent=2),
            file_name="query_analysis.json",
            mime="application/json"
        )
    else:
        st.info("👈 Enter a claim and click 'Analyze Claim' to see results")

st.divider()

# Examples and Tips
st.markdown("### 💡 Tips for Testing")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    **Good Test Cases:**
    - Policy announcements
    - Factual claims
    - Predictions
    - Mixed statements
    """)

with col2:
    st.markdown("""
    **What to Check:**
    - Are entities extracted correctly?
    - Is claim type accurate?
    - Is urgency reasonable?
    - Is JSON structure valid?
    """)

with col3:
    st.markdown("""
    **Edge Cases:**
    - Very short claims
    - Ambiguous statements
    - Multiple claims in one
    - Non-English text
    """)
