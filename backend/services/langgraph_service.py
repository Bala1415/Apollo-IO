from typing import Any, Dict
from ai.graph.graph import compiled_graph

def run_lead_analysis(company_domain: str, email: str, browser_history: dict = None) -> Dict[str, Any]:
    """
    Invokes the LangGraph pipeline for a specific lead.
    """
    initial_state = {
        "company_domain": company_domain,
        "email": email,
        "browser_history": browser_history or {},
        "research": {},
        "behavior": {},
        "company_fit": {},
        "qualification": {},
        "lead_score": {},
        "recommendation": {}
    }
    
    # Run the compiled graph
    result = compiled_graph.invoke(initial_state)
    return result
