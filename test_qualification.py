import os
import json
from dotenv import load_dotenv

# Load .env from the project root
load_dotenv()

import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai.agents.qualification_agent.node import qualification_node

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
    }
}

if __name__ == "__main__":
    os.environ["GROQ_API_KEY"] = ""
    
    print("Running Qualification Agent with mock state...")
    try:
        result = qualification_node(mock_state)
        print("\n--- QUALIFICATION RESULT ---")
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"\nError running node: {e}")
