"""
run_pipeline.py — End-to-end test runner for the full 6-agent Lead Intelligence Pipeline.

Runs all agents in sequence using a realistic mock input that simulates
data from the Chrome Extension.

Run:
    .venv\\Scripts\\Activate.ps1
    $env:PYTHONPATH="."
    python run_pipeline.py
"""
import os
import json
import logging
import time

from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

from ai.graph.graph import compiled_graph


def main():
    # Simulate input arriving from the Chrome Extension via FastAPI
    input_state = {
        "lead_id":        "lead_002",
        "company_domain": "langchain.com",
        "email":          "dev@acmecorp.io",

        # Raw browser data from Chrome extension
        "browser_data": {
            "current_domain": "langchain.com",
            "visited_domains": [
                {"domain": "openai.com",     "visit_count": 8, "path": "/docs"},
                {"domain": "langchain.com",  "visit_count": 6, "path": "/pricing"},
                {"domain": "langchain.com",  "visit_count": 3, "path": "/demo"},
                {"domain": "github.com",     "visit_count": 5, "path": "/langchain-ai/langchain"},
                {"domain": "groq.com",       "visit_count": 4, "path": "/"},
                {"domain": "aws.amazon.com", "visit_count": 3, "path": "/sagemaker"},
                {"domain": "huggingface.co", "visit_count": 2, "path": "/models"},
                {"domain": "stripe.com",     "visit_count": 1, "path": "/pricing"},
            ],
            "raw_urls": [
                "https://langchain.com/pricing",
                "https://langchain.com/demo",
                "https://openai.com/docs",
            ],
            "interest_categories": [
                {"category": "AI / ML", "score": 0.92},
                {"category": "Developer Tools", "score": 0.78},
            ],
        },

        # Interest profile from extension
        "interest_profile": {
            "summary": (
                "User is actively researching AI agent frameworks and LLM orchestration tools. "
                "Strong interest in LangChain pricing and demo pages, indicating late-stage evaluation."
            ),
            "top_topics": ["LLM Orchestration", "AI Agents", "Developer Tooling", "Cloud AI"],
            "scores": {
                "LLM Orchestration": 0.92,
                "AI Agents": 0.85,
                "Developer Tooling": 0.78,
                "Cloud AI": 0.55,
            },
        },

        # Empty — agents will populate these
        "research":      {},
        "behavior":      {},
        "company_fit":   {},
        "qualification": {},
        "lead_score":    {},
        "recommendation":{},
    }

    print("\n" + "=" * 70)
    print(f"  LEAD INTELLIGENCE PIPELINE")
    print(f"  Domain : {input_state['company_domain']}")
    print(f"  Lead   : {input_state['email']}")
    print("=" * 70 + "\n")

    start = time.time()
    try:
        final_state = compiled_graph.invoke(input_state)
    except Exception as e:
        print(f"\n[PIPELINE ERROR]: {e}")
        raise

    elapsed = round(time.time() - start, 2)

    # Print each agent's output section
    sections = [
        ("research",       "1. RESEARCH AGENT"),
        ("behavior",       "2. BEHAVIOR / INTENT AGENT"),
        ("company_fit",    "3. COMPANY FIT AGENT"),
        ("qualification",  "4. QUALIFICATION AGENT"),
        ("lead_score",     "5. LEAD SCORE AGENT"),
        ("recommendation", "6. RECOMMENDATION AGENT"),
    ]

    for key, title in sections:
        value = final_state.get(key, {})
        print(f"\n{'-' * 60}")
        print(f"  {title}")
        print(f"{'-' * 60}")
        print(json.dumps(value, indent=2))

    print("\n" + "=" * 70)
    print(f"  PIPELINE COMPLETE in {elapsed}s")

    # Quick summary
    rec   = final_state.get("recommendation", {})
    score = final_state.get("lead_score", {})
    qual  = final_state.get("qualification", {})
    fit   = final_state.get("company_fit", {})

    print(f"  Company Fit  : {fit.get('overall_fit', 'N/A')} ({fit.get('fit_score', 'N/A')}/100)")
    print(f"  Qualified    : {qual.get('qualified', 'N/A')}")
    print(f"  Lead Score   : {score.get('lead_score', 'N/A')}/100")
    print(f"  Priority     : {rec.get('priority', 'N/A')}")
    print(f"  Next Action  : {rec.get('next_action', 'N/A')}")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
