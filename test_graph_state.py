import sys
import json
from dotenv import load_dotenv
load_dotenv()
from ai.graph.graph import compiled_graph

def main():
    input_state = {
        "lead_id":        "test_001",
        "company_domain": "langchain.com",
        "email":          "test@langchain.com",
        "browser_data": {
            "current_domain": "langchain.com",
            "visited_domains": [],
            "raw_urls": [],
            "interest_categories": []
        },
        "interest_profile": {},
        "research":      {},
        "behavior":      {},
        "company_fit":   {},
        "qualification": {},
        "lead_score":    {},
        "recommendation":{},
    }
    
    final_state = compiled_graph.invoke(input_state)
    print("FINAL STATE RESEARCH:")
    print(json.dumps(final_state.get("research"), indent=2))

if __name__ == "__main__":
    main()
