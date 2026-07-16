import os
import json
from dotenv import load_dotenv

# Load .env from the project root
load_dotenv()

import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai.agents.recommendation_agent.node import recommendation_node

mock_state = {
    "company_domain": "example-ai-solutions.com",
    "industry": "B2B SaaS",
    "research": {
        "description": "Example AI Solutions provides cutting edge automation and AI tools for enterprise customers.",
        "founded": "2021",
        "employee_count": 250
    },
    "company_fit": {
        "size": "Mid-Market",
        "tech_stack": ["React", "Python", "LangChain"]
    },
    "browser_interest_profile": {
        "interests": ["AI Lead Generation", "Sales Automation", "CRM Integration"]
    },
    "qualification": {
        "qualified": True,
        "qualification_reason": "Strong ICP fit",
        "matching_features": ["B2B SaaS", "Mid-Market", "AI Automation"],
        "missing_features": [],
        "confidence": 0.95
    },
    "lead_score": {
        "lead_score": 83,
        "confidence": 95
    }
}

if __name__ == "__main__":
    # Force the Groq API key from the environment
    os.environ["GROQ_API_KEY"] = "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"
    
    print("Running Recommendation Agent with mock state...")
    try:
        result = recommendation_node(mock_state)
        print("\n--- RECOMMENDATION RESULT ---")
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"\nError running node: {e}")
