from typing import Dict, Any
from .similarity import calculate_list_similarity, calculate_similarity

def calculate_company_fit(state: Dict[str, Any]) -> Dict[str, float]:
    """
    Calculate deterministic company fit scores (Layer 1).
    Returns a dictionary of match scores from 0-100.
    """
    research = state.get("research", {})
    behavior = state.get("behavior", {})
    icp_rules = state.get("icp_rules", {})
    
    # Extract data safely
    company_data = research.get("company", {})
    tech_stack = research.get("technology", {})
    
    # Target ICP criteria (default or overridden)
    target_industries = icp_rules.get("target_industries", ["technology", "software", "saas", "developer tools"])
    target_tech = icp_rules.get("target_technologies", ["python", "typescript", "react", "node", "ai", "machine learning"])
    target_roles = icp_rules.get("target_roles", ["developer", "engineer", "cto", "architect"])
    
    # 1. Industry Match
    industry_match = 0.0
    company_industry = company_data.get("industry", "")
    if company_industry:
        industry_match = calculate_list_similarity([company_industry], target_industries)
    else:
        # Fallback to description keywords
        desc = company_data.get("description", "").lower()
        if any(t in desc for t in target_industries):
            industry_match = 70.0
            
    # 2. Technology Match
    tech_match = 0.0
    found_tech = []
    if tech_stack:
        for cat, tools in tech_stack.items():
            if tools:
                found_tech.extend(tools)
    if found_tech:
        tech_match = calculate_list_similarity(found_tech, target_tech)
        # Boost tech score if they have many tools
        if tech_match > 0:
            tech_match = min(tech_match * 1.5, 100.0)

    # 3. Persona Match
    persona_match = 0.0
    behavior_persona = behavior.get("persona", "").lower()
    if behavior_persona:
        persona_match = calculate_list_similarity([behavior_persona], target_roles)

    # 4. Market Match (Employee count proxy)
    market_match = 50.0 # Default
    emp_count = company_data.get("employee_count")
    if emp_count:
        if isinstance(emp_count, int) and emp_count > 50:
            market_match = 90.0
        elif isinstance(emp_count, str) and ("100" in emp_count or "1000" in emp_count):
            market_match = 90.0

    # 5. Business Model
    business_model_match = 50.0
    if "b2b" in (company_data.get("description", "") or "").lower():
        business_model_match = 80.0

    # 6. Intent Match
    intent_match = 0.0
    intent_level = behavior.get("commercial_intent", "").lower()
    if intent_level == "high":
        intent_match = 100.0
    elif intent_level == "medium":
        intent_match = 60.0
    elif intent_level == "low":
        intent_match = 20.0

    return {
        "industry_match": round(industry_match, 2),
        "technology_match": round(tech_match, 2),
        "persona_match": round(persona_match, 2),
        "market_match": round(market_match, 2),
        "business_model_match": round(business_model_match, 2),
        "intent_match": round(intent_match, 2)
    }
