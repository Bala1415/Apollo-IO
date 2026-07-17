"""
run_company_fit_agent.py — Standalone test runner for the Company Fit Agent.

Uses realistic mock output from the Research Agent and Behavior Agent
to validate the full hybrid Layer 1 + Layer 2 pipeline.

Run:
    .venv\\Scripts\\Activate.ps1
    $env:PYTHONPATH="."
    python run_company_fit_agent.py
"""
import os
import json
import logging
from typing import TypedDict, Dict, Any

from langgraph.graph import StateGraph, START, END
from ai.agents.company_fit import company_fit_node

from dotenv import load_dotenv
load_dotenv()

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
)

# ---------------------------------------------------------------------------
# GraphState
# ---------------------------------------------------------------------------
class GraphState(TypedDict):
    lead_id: str
    company_domain: str
    email: str
    research: Dict[str, Any]
    behavior: Dict[str, Any]
    company_fit: Dict[str, Any]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    workflow = StateGraph(GraphState)
    workflow.add_node("company_fit", company_fit_node)
    workflow.add_edge(START, "company_fit")
    workflow.add_edge("company_fit", END)
    app = workflow.compile()

    # --- Mock state: simulates output of Research Agent + Behavior Agent ---
    input_state: GraphState = {
        "lead_id":        "lead_003",
        "company_domain": "langchain.com",
        "email":          "dev@acmecorp.io",
        "company_fit":    {},

        # Simulated Research Agent output
        "research": {
            "company": {
                "name":           "LangChain",
                "website":        "https://langchain.com",
                "domain":         "langchain.com",
                "description":    "LangChain provides the engineering platform and open source frameworks developers use to build, test, and deploy reliable AI agents.",
                "founded_year":   "2023",
                "headquarters":   "San Francisco",
                "employee_count": None,
                "funding":        None,
            },
            "business": {
                "industry":          "Software",
                "sector":            "B2B SaaS",
                "business_model":    "SaaS",
                "revenue_model":     "Subscription",
                "pricing_model":     None,
                "target_market":     "Developer",
                "customer_segment":  "Developers",
                "sales_strategy":    None,
            },
            "products": [
                {
                    "name":         "LangSmith",
                    "category":     "AI Developer Tools",
                    "description":  "The Agent Engineering Platform",
                    "target_users": "Developers building AI agents",
                }
            ],
            "technology": {
                "cloud":     None,
                "ai_ml":     ["ChatGPT", "LangChain", "LangGraph", "LLM"],
                "frontend":  ["TypeScript"],
                "backend":   ["Go", "Python"],
                "crm":       None,
                "payments":  None,
                "devops":    None,
                "databases": None,
            },
            "customers": {
                "target_customers":  ["Software developers", "AI teams"],
                "customer_segments": ["Developers", "Engineering teams"],
                "industries_served": ["Software", "Technology"],
            },
            "competitors": None,
            "growth_signals": None,
            "social_links": {
                "linkedin": "https://www.linkedin.com/company/langchain/",
                "twitter":  "https://twitter.com/LangChain",
                "github":   None,
                "youtube":  "https://www.youtube.com/@LangChain",
            },
            "executive_summary": (
                "LangChain is a software company headquartered in San Francisco, founded in 2023. "
                "It provides an engineering platform and open source frameworks for developers to build, "
                "test, and deploy reliable AI agents. Their primary product, LangSmith, is an Agent "
                "Engineering Platform used by developer teams adopting LLM orchestration. "
                "The company targets the growing demand for AI-powered solutions in the developer ecosystem."
            ),
            "sources": ["https://langchain.com"],
        },

        # Simulated Behavior Agent output
        "behavior": {
            "primary_interest":   "AI Developer Tools",
            "secondary_interests": ["MLOps", "Cloud AI", "Developer Tooling"],
            "technology_interests": ["LangChain", "OpenAI", "AWS"],
            "business_functions": ["Engineering", "DevOps"],
            "industries":         None,
            "commercial_intent":  "very_high",
            "research_stage":     "decision",
            "decision_signals": [
                {"signal_type": "pricing_page",  "domain": "langchain.com", "weight": 1.0},
                {"signal_type": "demo_request",  "domain": "langchain.com", "weight": 1.0},
                {"signal_type": "pricing_page",  "domain": "stripe.com",    "weight": 1.0},
                {"signal_type": "documentation", "domain": "openai.com",    "weight": 0.5},
            ],
            "behavior_summary": (
                "The user is actively researching AI developer tools, particularly LangChain, "
                "and has shown strong interest in pricing and demo pages. They are also exploring "
                "open-source alternatives on GitHub and Hugging Face, indicating a high level of "
                "commercial intent. The user's behavior suggests they are in the decision stage "
                "of their buyer journey."
            ),
            "confidence": 0.9,
        },
    }

    print(f"\n--- Running Company Fit Agent for: {input_state['company_domain']} ---\n")

    try:
        final_state = app.invoke(input_state)
        print("\n--- Final State 'company_fit' output ---")
        print(json.dumps(final_state.get("company_fit", {}), indent=2))
    except Exception as e:
        print(f"\n[Error]: {e}")
        raise


if __name__ == "__main__":
    main()
