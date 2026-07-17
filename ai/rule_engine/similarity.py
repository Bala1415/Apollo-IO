"""
similarity.py — Semantic normalization utilities for rule engines.
"""
from typing import List

# Pre-defined semantic equivalence mappings
NORMALIZATION_MAP = {
    "developer platform": "developer tools",
    "developer framework": "developer tools",
    "ai framework": "developer tools",
    "llm platform": "developer tools",
    "artificial intelligence": "ai",
    "machine learning": "ai",
    "ml": "ai",
    "saas": "software",
    "fintech": "financial services",
    "b2b": "enterprise",
}

def normalize_term(term: str) -> str:
    """Normalize a single term using predefined mappings."""
    if not term:
        return ""
    term = term.lower().strip()
    return NORMALIZATION_MAP.get(term, term)

def calculate_similarity(term1: str, term2: str) -> float:
    """
    Calculate similarity between two terms. 
    1.0 = exact or semantic match.
    0.5 = partial match (e.g. one contains the other).
    0.0 = no match.
    """
    norm1 = normalize_term(term1)
    norm2 = normalize_term(term2)
    
    if norm1 == norm2:
        return 1.0
    
    # Partial match
    if len(norm1) > 3 and len(norm2) > 3:
        if norm1 in norm2 or norm2 in norm1:
            return 0.5
            
    return 0.0

def calculate_list_similarity(list1: List[str], list2: List[str]) -> float:
    """Calculate overlap between two lists of terms (returns 0-100 score)."""
    if not list1 or not list2:
        return 0.0
        
    score = 0.0
    for t1 in list1:
        best_match = 0.0
        for t2 in list2:
            match = calculate_similarity(t1, t2)
            if match > best_match:
                best_match = match
        score += best_match
        
    max_possible = max(len(list1), len(list2))
    return min((score / max_possible) * 100, 100.0)
