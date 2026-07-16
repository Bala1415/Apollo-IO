"""
similarity.py — Reusable similarity and keyword-overlap utilities.

All functions are pure (no side effects) and independently testable.
Designed to support the Rule Engine and future vector-based extensions.
"""
import re
from typing import List, Optional, Set


# ---------------------------------------------------------------------------
# 1. Text normalisation
# ---------------------------------------------------------------------------

def normalise(text: str) -> str:
    """Lowercase, strip punctuation, collapse whitespace."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def normalise_list(items: List[str]) -> List[str]:
    """Normalise every string in a list."""
    return [normalise(i) for i in items if i]


# ---------------------------------------------------------------------------
# 2. Keyword overlap scoring
# ---------------------------------------------------------------------------

def keyword_overlap_score(
    source: List[str],
    target: List[str],
    *,
    partial_match: bool = True,
) -> float:
    """
    Compute the fraction of `target` keywords found in `source`.

    Args:
        source: The list to search within (e.g. company technologies).
        target: The reference list (e.g. ICP preferred technologies).
        partial_match: If True, allow substring containment matches.

    Returns:
        Score in [0.0, 1.0]. Returns 0.0 if target is empty.
    """
    if not target:
        return 0.0

    src_norm = set(normalise_list(source))
    tgt_norm = normalise_list(target)

    matched = 0
    for t in tgt_norm:
        if t in src_norm:
            matched += 1
        elif partial_match and any(t in s or s in t for s in src_norm):
            matched += 0.6  # Partial credit

    return min(matched / len(tgt_norm), 1.0)


def bidirectional_overlap_score(
    list_a: List[str],
    list_b: List[str],
    *,
    partial_match: bool = True,
) -> float:
    """
    Symmetric overlap: average of A→B and B→A overlap scores.
    Avoids penalising a short list that perfectly matches a long one.
    """
    if not list_a or not list_b:
        return 0.0
    fwd = keyword_overlap_score(list_a, list_b, partial_match=partial_match)
    rev = keyword_overlap_score(list_b, list_a, partial_match=partial_match)
    return (fwd + rev) / 2.0


# ---------------------------------------------------------------------------
# 3. Set-based Jaccard similarity
# ---------------------------------------------------------------------------

def jaccard_similarity(set_a: Set[str], set_b: Set[str]) -> float:
    """
    Jaccard index: |A ∩ B| / |A ∪ B|.
    Returns 0.0 if both sets are empty.
    """
    if not set_a and not set_b:
        return 0.0
    intersection = set_a & set_b
    union = set_a | set_b
    return len(intersection) / len(union)


# ---------------------------------------------------------------------------
# 4. Exact / fuzzy single-value match
# ---------------------------------------------------------------------------

def exact_match(value: Optional[str], accepted: List[str]) -> bool:
    """Case-insensitive exact match of value against an accepted list."""
    if not value or not accepted:
        return False
    v = normalise(value)
    return any(v == normalise(a) for a in accepted)


def fuzzy_match(value: Optional[str], accepted: List[str]) -> float:
    """
    Returns a score 0.0–1.0:
      1.0  — exact match
      0.6  — substring match (value in accepted item or vice versa)
      0.0  — no match
    """
    if not value or not accepted:
        return 0.0
    v = normalise(value)
    accepted_norm = normalise_list(accepted)
    if v in accepted_norm:
        return 1.0
    if any(v in a or a in v for a in accepted_norm):
        return 0.6
    return 0.0


# ---------------------------------------------------------------------------
# 5. Score normalisation helpers
# ---------------------------------------------------------------------------

def to_100(score: float) -> float:
    """Convert a 0.0–1.0 score to 0–100, clamped."""
    return round(min(max(score * 100, 0.0), 100.0), 1)


def weighted_average(scores: List[float], weights: List[float]) -> float:
    """
    Compute a weighted average of scores.

    Args:
        scores:  List of raw scores (0–100).
        weights: Corresponding weights (must sum > 0).

    Returns:
        Weighted average, clamped to [0, 100].
    """
    if not scores or not weights or len(scores) != len(weights):
        return 0.0
    total_weight = sum(weights)
    if total_weight == 0:
        return 0.0
    return min(max(sum(s * w for s, w in zip(scores, weights)) / total_weight, 0.0), 100.0)


# ---------------------------------------------------------------------------
# 6. Fit label lookup
# ---------------------------------------------------------------------------

def score_to_fit_label(score: float) -> str:
    """Convert a numeric fit_score (0–100) to a qualitative label."""
    if score >= 80:
        return "Excellent Fit"
    elif score >= 60:
        return "Strong Fit"
    elif score >= 40:
        return "Moderate Fit"
    elif score >= 20:
        return "Poor Fit"
    else:
        return "Very Poor Fit"
