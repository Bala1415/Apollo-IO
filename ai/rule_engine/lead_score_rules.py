from typing import Dict, Any

def calculate_lead_score(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Pure Rule Engine to calculate lead score.
    Replaces LLM for Lead Score Agent.
    """
    company_fit = state.get("company_fit", {})
    behavior = state.get("behavior", {})
    qualification = state.get("qualification", {})
    
    # Base scores
    fit_score = company_fit.get("fit_score", 0.0)
    if not fit_score:
        rule_engine_scores = company_fit.get("rule_engine", {})
        if rule_engine_scores:
            fit_score = sum(rule_engine_scores.values()) / max(len(rule_engine_scores), 1)
            
    intent = behavior.get("commercial_intent", "").lower()
    intent_score = 50.0
    if intent == "high":
        intent_score = 100.0
    elif intent == "medium":
        intent_score = 75.0
    elif intent == "low":
        intent_score = 25.0
        
    is_qualified = qualification.get("qualified", False)
    qual_score = 100.0 if is_qualified else 20.0
    
    # Weighted math
    # 40% Fit, 40% Intent, 20% Qualification Status
    final_score = (fit_score * 0.4) + (intent_score * 0.4) + (qual_score * 0.2)
    
    # Cap to 0-100
    final_score = max(0, min(int(round(final_score)), 100))
    
    return {
        "lead_score": final_score,
        "confidence": 95
    }
