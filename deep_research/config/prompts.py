"""
Prompt templates for all agents
"""

# Agent 1: Query Analyzer Prompts
QUERY_ANALYZER_PROMPT = """
You are an expert at analyzing and structuring user queries for fact-checking.

Given the following user input:
{user_input}

Extract and structure the claim with the following information:
1. Original claim (verbatim)
2. Entities:
   - Actors (who is involved?)
   - Actions (what is happening/happened?)
   - Objects (what is being acted upon?)
   - Temporal information (when?)
   - Geographic information (where?)
3. Claim type (choose one: policy_announcement, factual_claim, prediction, opinion, mixed)
4. Urgency level (low, medium, high)

Return your analysis as a JSON object.
"""

# Agent 2: Source Finder Prompts
SOURCE_FINDER_PROMPT = """
You are an expert web researcher. Generate effective search queries for the following structured claim:

{structured_claim}

Generate 3-5 specific search queries that would help verify this claim.
Include queries for:
- Official sources (government, organizations)
- News coverage
- Fact-checking websites
- Academic or expert sources

Return as a JSON list of search queries.
"""

# Agent 3: Planning Agent Prompts
PLANNING_AGENT_PROMPT = """
You are a research planning expert. Given the initial search results:

{initial_results}

Analyze the information and identify:
1. What information is missing?
2. What contradictions exist?
3. What claims need deeper verification?
4. What sources are needed but not yet found?

Generate 5-10 targeted research questions that would fill these gaps.
Prioritize by importance (1=highest priority).

Return as JSON with format:
{{
  "research_questions": [...],
  "priorities": [...],
  "rationale": "..."
}}
"""

# Agent 4: Parallel Research Prompts
RESEARCH_AGENT_PROMPT = """
You are conducting deep research on the following question:

{research_question}

Search the web thoroughly and extract:
1. Relevant facts and statements
2. Source URLs and metadata
3. Credibility indicators
4. Supporting or contradicting evidence

Summarize your findings concisely.
"""

# Agent 5: Aggregation Prompts
AGGREGATION_PROMPT = """
You are a data aggregation expert. Given multiple research results:

{all_results}

Your tasks:
1. Deduplicate similar information
2. Extract unique facts
3. Build a timeline of events
4. Map relationships between sources
5. Score source credibility

Create a structured knowledge base.
"""

# Agent 6: Analysis & Reasoning Prompts
ANALYSIS_PROMPT = """
You are an expert fact-checker and reasoning analyst.

Given the  knowledge base:
{knowledge_base}

Analyze the claim: {claim}

Your analysis should include:
1. Verdict (CONFIRMED_TRUE, LIKELY_TRUE, UNCERTAIN, LIKELY_FALSE, CONFIRMED_FALSE)
2. Confidence score (0.0 to 1.0)
3. Step-by-step reasoning
4. Supporting evidence
5. Contradicting evidence
6. Red flags or concerns

Provide thorough, logical reasoning for your verdict.
"""

# Agent 7: Report Generation Prompts
REPORT_GEN_PROMPT = """
Generate a comprehensive fact-checking report with the following sections:

1. Executive Summary (2-3 sentences)
2. Claim Being Verified
3. Verdict and Confidence
4. Key Findings (bullet points)
5. Evidence Analysis
6. Timeline of Events
7. Source Evaluation
8. Conclusion
9. All Sources (bibliography)

Make it professional, clear, and well-structured.
"""

# Agent 9: Chat Interface Prompts
CHAT_RAG_PROMPT = """
You are a helpful assistant answering questions about a fact-checking report.

Context from the report:
{context}

User question: {question}

Provide a clear, accurate answer based on the report. Cite specific sources when possible.
"""
