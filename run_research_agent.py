import os
from typing import TypedDict, Dict, Any
from langgraph.graph import StateGraph, START, END
from ai.agents.research import research_node

# 1. Define the overall state for the Graph (or use the one from your project)
class GraphState(TypedDict):
    lead_id: str
    company_domain: str
    email: str
    browsing_summary: str
    research: Dict[str, Any]

def main():
    from dotenv import load_dotenv
    load_dotenv()

    # 2. Create the graph
    workflow = StateGraph(GraphState)

    # 3. Add our newly created research node
    workflow.add_node("research", research_node)

    # 4. Set the entry and exit points (For now, it's just one node)
    workflow.add_edge(START, "research")
    workflow.add_edge("research", END)

    # 5. Compile the graph into an executable app
    app = workflow.compile()

    # 6. Prepare some dummy data
    input_state = {
        "lead_id": "lead_001",
        "company_domain": "langchain.com",
        "email": "contact@langchain.com",
        "browsing_summary": "Looking into enterprise API pricing",
        "research": {}
    }

    print(f"--- Running Research Agent for domain: {input_state['company_domain']} ---\n")
    
    # 7. Invoke the graph
    try:
        final_state = app.invoke(input_state)
        print("\n--- Final State 'research' output ---")
        
        # Pretty print the research findings
        import json
        print(json.dumps(final_state.get("research", {}), indent=2))
        
    except Exception as e:
        print(f"\n[Error executing graph]: {e}")

if __name__ == "__main__":
    main()
