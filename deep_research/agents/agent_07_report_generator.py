"""
Agent 7: Report Generator Agent
Generates comprehensive reports in Markdown and PDF formats
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Any
from loguru import logger
import google.generativeai as genai
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from config.settings import Settings
from config.prompts import REPORT_GEN_PROMPT
from models.schemas import (
    AnalysisOutput, AggregatedData, Report, Verdict
)

# Configure Gemini
genai.configure(api_key=Settings.GOOGLE_API_KEY)

class ReportGeneratorAgent:
    """
    Agent 7: The Scribe - Creates detailed reports
    
    Capabilities:
    - Generate narrative report using LLM
    - Format as Markdown
    - Export to PDF
    - Structure data for presentation
    """
    
    def __init__(self):
        self.model = genai.GenerativeModel(
            model_name=Settings.DEFAULT_MODEL,
            generation_config={
                "temperature": Settings.TEMPERATURE,
                "max_output_tokens": Settings.MAX_TOKENS,
            }
        )
        logger.info("ReportGeneratorAgent initialized")

    def generate_report(self, claim: str, analysis: AnalysisOutput, data: AggregatedData) -> Report:
        """
        Generate full report from analysis and data
        
        Args:
            claim: Original claim
            analysis: Output from Agent 6
            data: Output from Agent 5
            
        Returns:
            Report object
        """
        logger.info("Generating report...")
        
        # Prepare context
        context = f"""
        Claim: {claim}
        Verdict: {analysis.verdict.value}
        Confidence: {analysis.confidence}
        Reasoning: {analysis.reasoning}
        
        Key Evidence:
        {json.dumps(analysis.evidence.model_dump(), indent=2)}
        
        Timeline:
        {json.dumps([t.model_dump() for t in data.timeline], indent=2)}
        """
        
        try:
            # Generate Narrative Sections
            prompt = REPORT_GEN_PROMPT + f"\n\nContext:\n{context}"
            
            # Add JSON guidance
            prompt += "\n\nReturn ONLY a valid JSON object with this structure:\n"
            prompt += json.dumps({
                "title": "string",
                "executive_summary": "string",
                "key_findings": ["list of strings"],
                "evidence_analysis": "string (markdown)",
                "source_evaluation": "string (markdown)",
                "conclusion": "string"
            }, indent=2)
            
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            
            # Extract JSON
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
                
            parsed = json.loads(text)
            
            # Create Report Object
            report = Report(
                title=parsed["title"],
                executive_summary=parsed["executive_summary"],
                claim=claim,
                verdict=analysis.verdict,
                confidence=analysis.confidence,
                key_findings=parsed["key_findings"],
                evidence_analysis=parsed["evidence_analysis"],
                timeline=data.timeline,
                source_evaluation=parsed["source_evaluation"],
                conclusion=parsed["conclusion"],
                sources_bibliography=[] # Populate from data if available
            )
            
            # Save Report Files
            self._save_markdown(report)
            self._save_pdf(report)
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating report: {e}")
            return self._create_fallback_report(claim, analysis)

    def _save_markdown(self, report: Report):
        """Save report as Markdown file"""
        filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        path = Settings.REPORTS_DIR / filename
        
        md_content = f"""# {report.title}

**Date:** {report.generated_at.strftime('%Y-%m-%d')}
**Verdict:** {report.verdict.value} (Confidence: {report.confidence:.0%})

## Executive Summary
{report.executive_summary}

## Claim Analysis
**Claim:** {report.claim}

## Key Findings
{chr(10).join([f'- {f}' for f in report.key_findings])}

## Evidence Analysis
{report.evidence_analysis}

## Timeline
{chr(10).join([f'- **{t.date}**: {t.event} ({t.source})' for t in report.timeline])}

## Source Evaluation
{report.source_evaluation}

## Conclusion
{report.conclusion}
"""
        with open(path, "w", encoding="utf-8") as f:
            f.write(md_content)
        
        logger.info(f"Saved Markdown report to {path}")

    def _save_pdf(self, report: Report):
        """Save report as PDF file"""
        filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        path = Settings.REPORTS_DIR / filename
        
        doc = SimpleDocTemplate(str(path), pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        story.append(Paragraph(report.title, styles['Title']))
        story.append(Spacer(1, 12))
        
        # Verdict
        story.append(Paragraph(f"Verdict: {report.verdict.value}", styles['Heading2']))
        story.append(Spacer(1, 12))
        
        # Exec Summary
        story.append(Paragraph("Executive Summary", styles['Heading2']))
        story.append(Paragraph(report.executive_summary, styles['Normal']))
        story.append(Spacer(1, 12))
        
        # Findings
        story.append(Paragraph("Key Findings", styles['Heading2']))
        for finding in report.key_findings:
            story.append(Paragraph(f"• {finding}", styles['Normal']))
        story.append(Spacer(1, 12))
        
        # Build PDF
        try:
            doc.build(story)
            logger.info(f"Saved PDF report to {path}")
        except Exception as e:
            logger.error(f"Failed to build PDF: {e}")

    def _create_fallback_report(self, claim: str, analysis: AnalysisOutput) -> Report:
        """Create basic report if generation fails"""
        return Report(
            title="Fact Check Report (Fallback)",
            executive_summary="Report generation failed. Please check logs.",
            claim=claim,
            verdict=analysis.verdict,
            confidence=analysis.confidence,
            key_findings=["Error generating full report"],
            evidence_analysis="N/A",
            timeline=[],
            source_evaluation="N/A",
            conclusion="N/A",
            sources_bibliography=[]
        )

if __name__ == "__main__":
    pass
