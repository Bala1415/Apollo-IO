"""
prompt.py — Unified LLM prompt template for the Research Agent.

Merges Fact Extraction and Business Reasoning into a single LLM call.
"""
from langchain_core.prompts import PromptTemplate

UNIFIED_RESEARCH_TEMPLATE = """\
You are a precise data extraction agent and senior business analyst specializing in B2B company intelligence.

Your task is to extract verifiable facts from the raw company data provided below, AND reason over those facts to produce a comprehensive, structured company intelligence report.

RULES:
- Extract ONLY information that is explicitly stated or can be safely deduced from the provided text.
- Do NOT generate false information. If a field cannot be found, leave it null or empty.
- Do NOT score, qualify, or recommend the company as a sales lead.
- The executive_summary must be a single, high-quality paragraph (4-6 sentences) that describes: what the company does, who it serves, what it sells, its business model, and its market position.

COMPANY DOMAIN: {company_domain}

RAW COMPANY DATA:
{merged_context}

{format_instructions}

Return ONLY the JSON object. No explanations, no markdown, no extra text.
"""

def get_unified_research_prompt() -> PromptTemplate:
    """Returns the unified research PromptTemplate."""
    return PromptTemplate(
        template=UNIFIED_RESEARCH_TEMPLATE,
        input_variables=["company_domain", "merged_context", "format_instructions"],
    )
