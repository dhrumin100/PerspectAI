"""
Agent 8: Infographic Generator Agent
Creates interactive visualizations for the report
"""

import json
import plotly.graph_objects as go
import plotly.express as px
from typing import List, Dict, Any
from loguru import logger
import networkx as nx

from config.settings import Settings
from models.schemas import AggregatedData, AnalysisOutput

class InfographicGeneratorAgent:
    """
    Agent 8: The Artist - Visualizes data
    
    Capabilities:
    - Create Truth Meter
    - Generate Timeline Chart
    - Build Network Graph
    - Create Credibility Distribution
    """
    
    def __init__(self):
        logger.info("InfographicGeneratorAgent initialized")

    def create_visualizations(self, analysis: AnalysisOutput, data: AggregatedData) -> Dict[str, Any]:
        """
        Generate Plotly figures for the report
        
        Args:
            analysis: Output from Agent 6
            data: Output from Agent 5
            
        Returns:
            Dictionary of Plotly figures
        """
        logger.info("Generating visualizations...")
        
        return {
            "truth_meter": self._create_truth_meter(analysis.confidence, analysis.verdict.value),
            "timeline_chart": self._create_timeline_chart(data.timeline),
            "credibility_chart": self._create_credibility_chart(data.credibility_map),
            "network_graph": self._create_network_graph(data.knowledge_graph)
        }

    def _create_truth_meter(self, confidence: float, verdict: str) -> go.Figure:
        """Create a gauge chart for truth score"""
        color = "green" if "TRUE" in verdict else "red" if "FALSE" in verdict else "orange"
        
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = confidence * 100,
            title = {'text': f"Verdict: {verdict}"},
            gauge = {
                'axis': {'range': [0, 100]},
                'bar': {'color': color},
                'steps': [
                    {'range': [0, 30], 'color': "lightgray"},
                    {'range': [30, 70], 'color': "gray"},
                    {'range': [70, 100], 'color': "darkgray"}
                ],
            }
        ))
        fig.update_layout(height=300)
        return fig

    def _create_timeline_chart(self, timeline: List[Any]) -> go.Figure:
        """Create a timeline chart"""
        if not timeline:
            return go.Figure()
            
        dates = [t.date for t in timeline]
        events = [t.event for t in timeline]
        sources = [t.source for t in timeline]
        
        fig = px.scatter(
            x=dates, 
            y=[1]*len(dates),
            text=events,
            hover_data={"Source": sources},
            title="Event Timeline"
        )
        fig.update_traces(textposition='top center', marker=dict(size=12, color='blue'))
        fig.update_yaxes(visible=False, showticklabels=False)
        fig.update_layout(height=300)
        return fig

    def _create_credibility_chart(self, credibility_map: Dict[str, float]) -> go.Figure:
        """Create a bar chart of source credibility"""
        if not credibility_map:
            return go.Figure()
            
        sources = list(credibility_map.keys())
        scores = list(credibility_map.values())
        
        fig = px.bar(
            x=sources,
            y=scores,
            title="Source Credibility Scores",
            labels={'x': 'Source', 'y': 'Credibility Score'},
            range_y=[0, 1]
        )
        return fig

    def _create_network_graph(self, kg: Any) -> go.Figure:
        """Create a network graph visualization"""
        # This is a simplified placeholder. 
        # Full network viz in Plotly is complex and requires node positions.
        # For now, we'll return an empty figure or simple scatter.
        return go.Figure()

if __name__ == "__main__":
    pass
