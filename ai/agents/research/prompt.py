"""
prompt.py — Two-stage LLM prompt templates for the Research Agent.

Stage 1: FACT_EXTRACTION  — extract only verifiable facts from raw web content.
Stage 2: BUSINESS_REASONING — reason over those facts to produce business intelligence.
"""
from langchain_core.prompts import PromptTemplate

# ---------------------------------------------------------------------------
# Stage 1 — Fact Extraction Prompt
# ---------------------------------------------------------------------------

FACT_EXTRACTION_TEMPLATE = """\
You are a precise data extraction agent. Your ONLY job is to extract verifiable facts from the raw company data provided below.

RULES:
- Extract ONLY information that is explicitly stated in the provided text.
- Do NOT infer, guess, assume, or generate information that is not present.
- Do NOT classify the company or make business judgments.
- Do NOT score, qualify, or recommend anything.
- If a field cannot be found, leave it null or empty.

COMPANY DOMAIN: {company_domain}

RAW COMPANY DATA:
{merged_context}

{format_instructions}

Return ONLY the JSON object. No explanations, no markdown, no extra text.
"""

# ---------------------------------------------------------------------------
# Stage 2 — Business Reasoning Prompt
# ---------------------------------------------------------------------------

BUSINESS_REASONING_TEMPLATE = """\
You are a senior business analyst specializing in B2B company intelligence.

You have been given structured facts already extracted from a company's website and online presence.
Your task is to reason over ONLY these facts and produce a comprehensive company intelligence report.

RULES:
- Use ONLY the facts provided below. Do NOT introduce external knowledge not grounded in these facts.
- Do NOT score, qualify, or recommend the company as a sales lead.
- Do NOT make ICP (Ideal Customer Profile) assessments.
- DO reason about business model, target market, growth signals, and competitive positioning based solely on the facts.
- Be specific. Avoid generic filler like "the company provides solutions for businesses."
- The executive_summary must be a single, high-quality paragraph (4-6 sentences) that describes: what the company does, who it serves, what it sells, its business model, and its market position.

COMPANY DOMAIN: {company_domain}

EXTRACTED FACTS:
{extracted_facts}

{format_instructions}

Return ONLY the JSON object. No explanations, no markdown, no extra text.
"""

# ---------------------------------------------------------------------------
# Factory functions
# ---------------------------------------------------------------------------

def get_fact_extraction_prompt() -> PromptTemplate:
    """Returns the Stage 1 fact extraction PromptTemplate."""
    return PromptTemplate(
        template=FACT_EXTRACTION_TEMPLATE,
        input_variables=["company_domain", "merged_context", "format_instructions"],
    )


def get_business_reasoning_prompt() -> PromptTemplate:
    """Returns the Stage 2 business reasoning PromptTemplate."""
    return PromptTemplate(
        template=BUSINESS_REASONING_TEMPLATE,
        input_variables=["company_domain", "extracted_facts", "format_instructions"],
    )
