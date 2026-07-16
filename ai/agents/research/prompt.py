from langchain_core.prompts import PromptTemplate

RESEARCH_PROMPT_TEMPLATE = """
You are an expert Research Agent responsible for gathering factual information about a company.

Your task is to analyze the provided raw website content and news information to extract structured data about the company.
You must ONLY gather factual information. DO NOT classify, score, qualify, or make recommendations about the lead.

Company Domain: {company_domain}

Raw Website Content:
{website_content}

Recent News:
{news_content}

{format_instructions}

Extract the requested information accurately. If a specific piece of information cannot be found in the provided context, leave it null or empty as appropriate according to the schema. Do not invent or guess information.
"""

def get_research_prompt() -> PromptTemplate:
    """
    Returns the PromptTemplate for the Research Agent.
    """
    return PromptTemplate(
        template=RESEARCH_PROMPT_TEMPLATE,
        input_variables=["company_domain", "website_content", "news_content"],
        partial_variables={"format_instructions": ""} # Will be populated by the parser
    )
