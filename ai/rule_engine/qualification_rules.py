from typing import Dict, Any

def evaluate_qualification(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Pure Rule Engine to determine lead qualification.
    Replaces LLM for Qualification Agent.
    """
    company_fit = state.get("company_fit", {})
    behavior = state.get("behavior", {})
    
    rule_engine_scores = company_fit.get("rule_engine", {})
    overall_fit_label = company_fit.get("overall_fit", "").lower()
    
    intent = behavior.get("commercial_intent", "").lower()
    stage = behavior.get("research_stage", "").lower()
    
    matching_features = []
    missing_features = []
    
    # Analyze rule engine scores
    if rule_engine_scores:
        if rule_engine_scores.get("industry_match", 0) > 60:
            matching_features.append("Strong industry alignment")
        else:
            missing_features.append("Weak industry alignment")
            
        if rule_engine_scores.get("technology_match", 0) > 60:
            matching_features.append("Compatible technology stack")
            
        if rule_engine_scores.get("intent_match", 0) > 70:
            matching_features.append("High commercial intent signals")
            
    # Intent and Stage
    if intent == "high":
        matching_features.append(f"High intent ({stage} stage)")
    elif intent == "low":
        missing_features.append("Low commercial intent")
        
    # Fit Label fallback
    if "excellent" in overall_fit_label or "strong" in overall_fit_label:
        matching_features.append("Overall company fit is strong")
    elif "poor" in overall_fit_label:
        missing_features.append("Overall company fit is poor")

    # Qualification Logic
    qualified = False
    reasons = []
    
    # Must have decent fit OR high intent to be qualified
    avg_score = 0
    if rule_engine_scores:
        avg_score = sum(rule_engine_scores.values()) / max(len(rule_engine_scores), 1)
        
    if avg_score >= 50.0 and intent != "low":
        qualified = True
        reasons.append("Company meets baseline fit criteria and shows adequate intent.")
    elif intent == "high" and avg_score >= 30.0:
        qualified = True
        reasons.append("High commercial intent overrides moderate fit scores.")
    else:
        reasons.append("Company does not meet minimum fit criteria or intent is too low.")
        
    return {
        "qualified": qualified,
        "qualification_reason": " ".join(reasons),
        "matching_features": matching_features,
        "missing_features": missing_features,
        "confidence": 0.9 # Rule engine is highly confident in its deterministic output
    }
