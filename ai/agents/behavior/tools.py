"""
tools.py — Browser data preprocessing tools for the Intent Analysis Agent.

Responsibilities:
  - Normalize and validate raw browser_data and interest_profile payloads
  - Compute visit frequency signals and domain categorization
  - Detect high-intent decision signals from visited URLs
  - Produce a clean, structured text context for the LLM prompt

Each function is stateless and independently testable.
"""
import logging
import re
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants — Decision signal URL patterns
# ---------------------------------------------------------------------------

DECISION_SIGNAL_PATTERNS: List[Tuple[str, str, float]] = [
    # (url_pattern_regex, signal_type, weight)
    (r"pricing|plans|price",          "pricing_page",    1.0),
    (r"demo|book-demo|schedule-demo", "demo_request",    1.0),
    (r"contact.?sales|talk.?to.?sales|sales", "contact_sales", 0.95),
    (r"checkout|buy|purchase|order",  "checkout",        0.9),
    (r"free.?trial|start.?free|try.?free", "free_trial", 0.85),
    (r"vs|versus|compare|comparison|alternatives", "comparison_page", 0.8),
    (r"case.?stud|customer.?stor|success.?stor", "case_study", 0.7),
    (r"product|features|platform|solution", "product_page", 0.65),
    (r"docs|documentation|api.?ref|developer", "documentation", 0.5),
    (r"blog|article|learn|guide|tutorial", "educational_content", 0.3),
]

# ---------------------------------------------------------------------------
# Category mapping — domain → business category
# ---------------------------------------------------------------------------

DOMAIN_CATEGORY_MAP: Dict[str, str] = {
    # AI / ML
    "openai.com": "AI Tools",
    "anthropic.com": "AI Tools",
    "huggingface.co": "AI / ML",
    "langchain.com": "AI Developer Tools",
    "groq.com": "AI Infrastructure",
    "replicate.com": "AI Infrastructure",
    "together.ai": "AI Infrastructure",
    "cohere.com": "AI Tools",
    # Cloud
    "aws.amazon.com": "Cloud Infrastructure",
    "cloud.google.com": "Cloud Infrastructure",
    "azure.microsoft.com": "Cloud Infrastructure",
    "vercel.com": "Cloud / Hosting",
    "netlify.com": "Cloud / Hosting",
    "digitalocean.com": "Cloud Infrastructure",
    # DevOps / Dev Tools
    "github.com": "Developer Tools",
    "gitlab.com": "Developer Tools",
    "docker.com": "DevOps",
    "kubernetes.io": "DevOps",
    "terraform.io": "DevOps",
    "datadog.com": "Observability",
    "sentry.io": "Observability",
    # CRM / Sales
    "salesforce.com": "CRM",
    "hubspot.com": "CRM / Marketing",
    "pipedrive.com": "CRM",
    "apollo.io": "Sales Intelligence",
    "outreach.io": "Sales Engagement",
    "salesloft.com": "Sales Engagement",
    # Productivity
    "notion.so": "Productivity",
    "airtable.com": "Productivity",
    "linear.app": "Project Management",
    "asana.com": "Project Management",
    "slack.com": "Communication",
    # Payments / Finance
    "stripe.com": "Payments",
    "brex.com": "Finance",
    "ramp.com": "Finance",
    # Analytics / BI
    "tableau.com": "Analytics",
    "looker.com": "Analytics",
    "mixpanel.com": "Analytics",
    "segment.com": "Data / CDP",
    # Database / Data
    "snowflake.com": "Data Warehouse",
    "databricks.com": "Data / ML",
    "mongodb.com": "Database",
    "supabase.com": "Database",
}

# ---------------------------------------------------------------------------
# 1. Normalise raw GraphState browser_data payload
# ---------------------------------------------------------------------------

def normalize_browser_data(browser_data: Any) -> Dict[str, Any]:
    """
    Accepts browser_data in multiple possible shapes and normalises to a
    canonical dict with consistent keys.

    Expected canonical shape:
    {
        "visited_domains": [{"domain": str, "visit_count": int, "path": str}],
        "interest_categories": [{"category": str, "score": float}],
        "current_domain": str | None,
        "raw_urls": [str],
    }
    """
    if not browser_data:
        logger.warning("browser_data is empty or None")
        return {
            "visited_domains": [],
            "interest_categories": [],
            "current_domain": None,
            "raw_urls": [],
        }

    if isinstance(browser_data, str):
        # Treat plain string as a comma-separated list of URLs/domains
        return {
            "visited_domains": [{"domain": d.strip(), "visit_count": 1, "path": ""} for d in browser_data.split(",") if d.strip()],
            "interest_categories": [],
            "current_domain": None,
            "raw_urls": [d.strip() for d in browser_data.split(",") if d.strip()],
        }

    if isinstance(browser_data, dict):
        return {
            "visited_domains": browser_data.get("visited_domains") or [],
            "interest_categories": browser_data.get("interest_categories") or browser_data.get("interests") or [],
            "current_domain": browser_data.get("current_domain") or browser_data.get("domain"),
            "raw_urls": browser_data.get("raw_urls") or browser_data.get("urls") or [],
        }

    logger.warning(f"Unexpected browser_data type: {type(browser_data)}")
    return {"visited_domains": [], "interest_categories": [], "current_domain": None, "raw_urls": []}


def normalize_interest_profile(interest_profile: Any) -> Dict[str, Any]:
    """
    Normalise interest_profile from GraphState to a canonical dict.

    Canonical shape:
    {
        "summary": str | None,
        "top_topics": [str],
        "scores": {"topic": float},
    }
    """
    if not interest_profile:
        return {"summary": None, "top_topics": [], "scores": {}}

    if isinstance(interest_profile, str):
        return {"summary": interest_profile, "top_topics": [], "scores": {}}

    if isinstance(interest_profile, dict):
        return {
            "summary": interest_profile.get("summary") or interest_profile.get("description"),
            "top_topics": interest_profile.get("top_topics") or interest_profile.get("topics") or [],
            "scores": interest_profile.get("scores") or interest_profile.get("interest_scores") or {},
        }

    return {"summary": str(interest_profile), "top_topics": [], "scores": {}}


# ---------------------------------------------------------------------------
# 2. Visit frequency analysis
# ---------------------------------------------------------------------------

def compute_visit_frequency(visited_domains: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Deduplicate domain visits, aggregate visit counts, and sort by frequency.
    Returns a ranked list of {domain, visit_count, category}.
    """
    domain_counts: Dict[str, int] = {}
    for entry in visited_domains:
        domain = (entry.get("domain") or "").strip().lower()
        count = int(entry.get("visit_count") or 1)
        if domain:
            domain_counts[domain] = domain_counts.get(domain, 0) + count

    ranked = sorted(domain_counts.items(), key=lambda x: x[1], reverse=True)
    result = [
        {
            "domain": domain,
            "visit_count": count,
            "category": DOMAIN_CATEGORY_MAP.get(domain, "Unknown"),
        }
        for domain, count in ranked
    ]
    logger.info(f"Visit frequency computed for {len(result)} unique domains")
    return result


# ---------------------------------------------------------------------------
# 3. Decision signal detection
# ---------------------------------------------------------------------------

def detect_decision_signals(raw_urls: List[str], visited_domains: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Scan URL paths and domain entries for high-intent behavioral patterns.
    Returns a list of detected signals with type, domain, and weight.
    """
    signals: List[Dict[str, Any]] = []
    seen: set = set()

    all_urls = list(raw_urls)
    for entry in visited_domains:
        path = entry.get("path", "")
        domain = entry.get("domain", "")
        if path:
            all_urls.append(f"{domain}/{path}")

    for url in all_urls:
        url_lower = url.lower()
        for pattern, signal_type, weight in DECISION_SIGNAL_PATTERNS:
            if re.search(pattern, url_lower):
                key = f"{signal_type}:{_extract_domain(url)}"
                if key not in seen:
                    seen.add(key)
                    signals.append({
                        "signal_type": signal_type,
                        "domain": _extract_domain(url),
                        "weight": weight,
                    })
                    logger.info(f"Decision signal detected: {signal_type} on {_extract_domain(url)}")
                break  # First matching pattern wins per URL

    # Sort by descending weight
    return sorted(signals, key=lambda s: s["weight"], reverse=True)


def _extract_domain(url: str) -> str:
    """Extract domain from a URL string."""
    url = re.sub(r"https?://", "", url)
    return url.split("/")[0]


# ---------------------------------------------------------------------------
# 4. Context builder
# ---------------------------------------------------------------------------

def build_behavior_context(
    normalized_browser: Dict[str, Any],
    normalized_profile: Dict[str, Any],
    visit_frequency: List[Dict[str, Any]],
    decision_signals: List[Dict[str, Any]],
    email: Optional[str],
    domain: Optional[str],
) -> str:
    """
    Merge all preprocessed behavioral signals into a clean structured text block
    to be sent to the LLM for behavioral reasoning.
    """
    sections = []

    # Basic context
    basics = []
    if email:
        basics.append(f"  Email: {email}")
    if domain:
        basics.append(f"  Company Domain: {domain}")
    if normalized_browser.get("current_domain"):
        basics.append(f"  Current Website: {normalized_browser['current_domain']}")
    if basics:
        sections.append("=== LEAD CONTEXT ===\n" + "\n".join(basics))

    # Interest profile
    if normalized_profile.get("summary"):
        sections.append(f"=== INTEREST PROFILE SUMMARY ===\n  {normalized_profile['summary']}")

    if normalized_profile.get("top_topics"):
        topics = ", ".join(normalized_profile["top_topics"])
        sections.append(f"=== TOP INTEREST TOPICS ===\n  {topics}")

    if normalized_profile.get("scores"):
        scores_text = "\n".join(
            f"  {topic}: {score}" for topic, score in normalized_profile["scores"].items()
        )
        sections.append(f"=== INTEREST SCORES ===\n{scores_text}")

    # Visit frequency
    if visit_frequency:
        freq_lines = [
            f"  {i+1}. {entry['domain']} — {entry['visit_count']} visit(s) [{entry['category']}]"
            for i, entry in enumerate(visit_frequency[:20])  # Top 20 domains
        ]
        sections.append("=== VISITED DOMAINS (by frequency) ===\n" + "\n".join(freq_lines))

    # Decision signals
    if decision_signals:
        sig_lines = [
            f"  [{s['signal_type'].upper()}] on {s['domain']} (weight: {s['weight']})"
            for s in decision_signals
        ]
        sections.append("=== HIGH-INTENT SIGNALS DETECTED ===\n" + "\n".join(sig_lines))
    else:
        sections.append("=== HIGH-INTENT SIGNALS DETECTED ===\n  None detected.")

    # Raw interest categories from browser data
    interest_cats = normalized_browser.get("interest_categories", [])
    if interest_cats:
        if isinstance(interest_cats[0], dict):
            cat_lines = [
                f"  {c.get('category', 'Unknown')}: {c.get('score', 'N/A')}"
                for c in interest_cats
            ]
        else:
            cat_lines = [f"  {c}" for c in interest_cats]
        sections.append("=== BROWSER INTEREST CATEGORIES ===\n" + "\n".join(cat_lines))

    return "\n\n".join(sections)
