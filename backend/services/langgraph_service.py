from typing import Any, Dict
from ai.graph.graph import compiled_graph

def run_lead_analysis(company_domain: str, email: str, browser_history: dict = None) -> Dict[str, Any]:
    """
    Invokes the LangGraph pipeline for a specific lead.
    """
    company_domain = company_domain or ""
    
    # Fallback: Extract company name from email if domain is missing or unknown
    if (not company_domain or company_domain == "unknown.com") and email:
        username = email.split("@")[0]
        parts = username.split(".")
        # e.g. firstname.lastname.zuntra -> zuntra
        extracted = parts[-1] if len(parts) > 1 else parts[0]
        
        from ai.services.llm_service import intelligently_resolve_domain
        company_domain = intelligently_resolve_domain(extracted)
        
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
