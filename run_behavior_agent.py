"""
run_behavior_agent.py — Standalone test runner for the Intent Analysis Agent.

Tests the agent in isolation using realistic mock browser_data and interest_profile.
Run:
    $env:GROQ_API_KEY="your-key"
    python run_behavior_agent.py
"""
import os
import json
import logging
from typing import TypedDict, Dict, Any, List

from langgraph.graph import StateGraph, START, END
from ai.agents.behavior import behavior_node

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
)

# ---------------------------------------------------------------------------
# GraphState definition
# ---------------------------------------------------------------------------
class GraphState(TypedDict):
    lead_id: str
    company_domain: str
    email: str
    browser_data: Dict[str, Any]
    interest_profile: Dict[str, Any]
    research: Dict[str, Any]
    behavior: Dict[str, Any]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    from dotenv import load_dotenv
    load_dotenv()

    # --- Build graph ---
    workflow = StateGraph(GraphState)
    workflow.add_node("behavior", behavior_node)
    workflow.add_edge(START, "behavior")
    workflow.add_edge("behavior", END)
    app = workflow.compile()

    # --- Realistic mock input ---
    input_state: GraphState = {
        "lead_id": "lead_002",
        "company_domain": "acmecorp.io",
        "email": "dev@acmecorp.io",
        "research": {},
        "behavior": {},
        "browser_data": {
            "current_domain": "langchain.com",
            "visited_domains": [
                {"domain": "openai.com",    "visit_count": 8,  "path": "/docs"},
                {"domain": "langchain.com", "visit_count": 6,  "path": "/pricing"},
                {"domain": "langchain.com", "visit_count": 3,  "path": "/demo"},
                {"domain": "github.com",    "visit_count": 5,  "path": "/langchain-ai/langchain"},
                {"domain": "groq.com",      "visit_count": 4,  "path": "/"},
                {"domain": "aws.amazon.com","visit_count": 3,  "path": "/sagemaker"},
                {"domain": "huggingface.co","visit_count": 2,  "path": "/models"},
                {"domain": "notion.so",     "visit_count": 2,  "path": "/"},
                {"domain": "stripe.com",    "visit_count": 1,  "path": "/pricing"},
            ],
            "raw_urls": [
                "https://langchain.com/pricing",
                "https://langchain.com/demo",
                "https://openai.com/docs",
                "https://github.com/langchain-ai/langchain",
                "https://huggingface.co/models",
            ],
            "interest_categories": [
                {"category": "AI / ML", "score": 0.92},
                {"category": "Developer Tools", "score": 0.78},
                {"category": "Cloud Infrastructure", "score": 0.55},
            ],
        },
        "interest_profile": {
            "summary": (
                "User is actively researching AI agent frameworks and LLM orchestration tools. "
                "Showed strong interest in LangChain pricing and demo pages, indicating "
                "late-stage evaluation. Also exploring open-source alternatives on GitHub "
                "and Hugging Face."
            ),
            "top_topics": ["LLM Orchestration", "AI Agents", "Developer Tooling", "Cloud AI"],
            "scores": {
                "LLM Orchestration": 0.92,
                "AI Agents": 0.85,
                "Developer Tooling": 0.78,
                "MLOps": 0.60,
                "Cloud AI": 0.55,
            },
        },
    }

    print(f"\n--- Running Intent Analysis Agent for: {input_state['email']} ---\n")

    try:
        final_state = app.invoke(input_state)
        print("\n--- Final State 'behavior' output ---")
        print(json.dumps(final_state.get("behavior", {}), indent=2))
    except Exception as e:
        print(f"\n[Error]: {e}")


if __name__ == "__main__":
    main()
