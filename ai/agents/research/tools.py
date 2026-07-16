"""
tools.py — Web crawling, metadata extraction, technology detection, and news retrieval
for the Research Agent.

Each function is independently testable and stateless.
"""
import logging
import re
import json
import time
from typing import Dict, List, Any, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from .schemas import TechnologyStack, SocialLinks

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

# Priority page slugs to discover from the homepage
TARGET_PAGE_SLUGS = [
    "about", "about-us", "company",
    "products", "product",
    "services", "service",
    "solutions", "solution",
    "customers", "case-studies", "clients",
    "pricing", "plans",
    "careers", "jobs", "hiring",
    "blog", "news", "press",
    "contact", "contact-us",
    "platform", "features",
]

MAX_PAGES = 8
PAGE_CHAR_LIMIT = 2500

# ---------------------------------------------------------------------------
# Technology detection dictionary
# ---------------------------------------------------------------------------

TECH_PATTERNS: Dict[str, List[str]] = {
    "cloud": ["AWS", "Amazon Web Services", "Google Cloud", "GCP", "Azure", "Microsoft Azure", "Cloudflare", "Vercel", "Heroku", "DigitalOcean"],
    "ai_ml": ["OpenAI", "ChatGPT", "Anthropic", "Claude", "LangChain", "LangGraph", "Hugging Face", "TensorFlow", "PyTorch", "Gemini", "GPT-4", "LLM", "AI-powered", "machine learning", "deep learning"],
    "frontend": ["React", "Next.js", "Vue", "Angular", "Svelte", "TypeScript", "JavaScript", "Tailwind", "Gatsby", "Remix"],
    "backend": ["Node.js", "FastAPI", "Django", "Flask", "Rails", "Spring Boot", "Go", "Rust", "Python", "GraphQL", "REST API"],
    "crm": ["HubSpot", "Salesforce", "Pipedrive", "Zoho", "Intercom", "Zendesk", "Freshdesk"],
    "payments": ["Stripe", "PayPal", "Braintree", "Square", "Chargebee", "Recurly"],
    "devops": ["Docker", "Kubernetes", "GitHub Actions", "CircleCI", "Jenkins", "Terraform", "Helm", "GitLab CI"],
    "databases": ["PostgreSQL", "MySQL", "MongoDB", "Redis", "Elasticsearch", "Snowflake", "BigQuery", "Pinecone", "Supabase", "PlanetScale"],
}

# ---------------------------------------------------------------------------
# Core helpers
# ---------------------------------------------------------------------------

def _fetch_page(url: str, timeout: int = 10) -> Optional[str]:
    """Fetch a URL and return raw HTML, or None on failure."""
    try:
        response = requests.get(url, timeout=timeout, headers=REQUEST_HEADERS)
        response.raise_for_status()
        return response.text
    except Exception as e:
        logger.warning(f"Failed to fetch {url}: {e}")
        return None


def _extract_clean_text(html: str, char_limit: int = PAGE_CHAR_LIMIT) -> str:
    """Convert raw HTML to clean readable text, trimmed to char_limit."""
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header", "noscript", "svg", "form"]):
        tag.extract()
    text = soup.get_text(separator=" ", strip=True)
    # Collapse excessive whitespace
    text = re.sub(r"\s{2,}", " ", text)
    return text[:char_limit]


# ---------------------------------------------------------------------------
# 1. Website Discovery
# ---------------------------------------------------------------------------

def discover_website(domain: str) -> str:
    """
    Returns the canonical HTTPS URL for the given domain.
    Tries https:// first, falls back to http:// if needed.
    """
    if domain.startswith("http"):
        return domain
    url = f"https://{domain}"
    try:
        resp = requests.head(url, timeout=8, headers=REQUEST_HEADERS, allow_redirects=True)
        return resp.url  # Return final URL after redirects
    except Exception:
        return url


# ---------------------------------------------------------------------------
# 2. Multi-Page Crawler
# ---------------------------------------------------------------------------

def _discover_internal_links(homepage_html: str, base_url: str) -> List[Tuple[str, str]]:
    """
    Find internal links that match target page slugs.
    Returns list of (page_name, full_url) tuples.
    """
    soup = BeautifulSoup(homepage_html, "html.parser")
    found: Dict[str, str] = {}
    base_domain = urlparse(base_url).netloc

    for tag in soup.find_all("a", href=True):
        href = tag["href"].strip()
        full_url = urljoin(base_url, href)
        parsed = urlparse(full_url)

        # Only internal pages
        if parsed.netloc and parsed.netloc != base_domain:
            continue

        path = parsed.path.lower().strip("/")
        for slug in TARGET_PAGE_SLUGS:
            if slug in path and path not in ("", "/"):
                # Use the first matching slug as page label
                label = slug.replace("-", "_")
                if label not in found:
                    found[label] = full_url
                break

    return list(found.items())


def crawl_website(base_url: str) -> Dict[str, str]:
    """
    Crawl the company website across multiple pages.

    1. Fetches the homepage.
    2. Discovers internal links matching target slugs.
    3. Fetches up to MAX_PAGES pages concurrently.

    Returns a dict of {page_name: clean_text_content}.
    """
    pages: Dict[str, str] = {}

    # --- Homepage ---
    logger.info(f"Crawling homepage: {base_url}")
    homepage_html = _fetch_page(base_url)
    if not homepage_html:
        logger.warning("Could not fetch homepage.")
        return pages

    pages["home"] = _extract_clean_text(homepage_html)

    # --- Discover internal links ---
    internal_links = _discover_internal_links(homepage_html, base_url)
    logger.info(f"Discovered {len(internal_links)} internal pages to crawl: {[l for l, _ in internal_links]}")

    # Limit to MAX_PAGES - 1 (homepage already counted)
    links_to_fetch = internal_links[: MAX_PAGES - 1]

    # --- Concurrent fetch ---
    def fetch_and_extract(label_url: Tuple[str, str]) -> Tuple[str, str]:
        label, url = label_url
        html = _fetch_page(url)
        if html:
            return label, _extract_clean_text(html)
        return label, ""

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(fetch_and_extract, lu): lu for lu in links_to_fetch}
        for future in as_completed(futures):
            label, content = future.result()
            if content:
                pages[label] = content
                logger.info(f"Crawled page: '{label}' ({len(content)} chars)")
            else:
                logger.warning(f"Empty content for page: '{label}'")

    logger.info(f"Total pages crawled: {len(pages)} — {list(pages.keys())}")
    return pages


# ---------------------------------------------------------------------------
# 3. Metadata Extraction
# ---------------------------------------------------------------------------

def extract_metadata(homepage_html: str, base_url: str) -> Dict[str, Any]:
    """
    Extract structured metadata from the homepage HTML.

    Looks for:
    - <meta> tags (description, og:description, og:site_name)
    - schema.org Organization JSON-LD
    - Social media links
    - Contact emails
    """
    soup = BeautifulSoup(homepage_html, "html.parser")
    meta: Dict[str, Any] = {}

    # --- Meta tags ---
    for tag in soup.find_all("meta"):
        name = tag.get("name", "").lower() or tag.get("property", "").lower()
        content = tag.get("content", "").strip()
        if not content:
            continue
        if name in ("description", "og:description"):
            meta.setdefault("description", content)
        elif name == "og:site_name":
            meta.setdefault("company_name", content)

    # --- schema.org JSON-LD ---
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string or "")
            if isinstance(data, list):
                data = data[0]
            if data.get("@type") in ("Organization", "Corporation", "WebSite"):
                meta.setdefault("company_name", data.get("name"))
                meta.setdefault("description", data.get("description"))
                meta["founded_year"] = data.get("foundingDate")
                meta["headquarters"] = data.get("address", {}).get("addressLocality") if isinstance(data.get("address"), dict) else None
                meta["employee_count"] = data.get("numberOfEmployees")
        except Exception:
            pass

    # --- Social links ---
    social: Dict[str, Optional[str]] = {
        "linkedin": None, "twitter": None, "github": None, "youtube": None
    }
    for tag in soup.find_all("a", href=True):
        href = tag["href"].lower()
        if "linkedin.com" in href:
            social["linkedin"] = tag["href"]
        elif "twitter.com" in href or "x.com" in href:
            social["twitter"] = tag["href"]
        elif "github.com" in href:
            social["github"] = tag["href"]
        elif "youtube.com" in href:
            social["youtube"] = tag["href"]

    meta["social_links"] = social

    # --- Contact email ---
    email_pattern = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")
    page_text = soup.get_text()
    emails = email_pattern.findall(page_text)
    # Filter out image/asset emails
    real_emails = [e for e in emails if not any(ext in e for ext in [".png", ".jpg", ".svg", ".gif"])]
    if real_emails:
        meta["contact_email"] = real_emails[0]

    return meta


# ---------------------------------------------------------------------------
# 4. Technology Detection
# ---------------------------------------------------------------------------

def detect_technologies(all_text: str) -> TechnologyStack:
    """
    Scan all crawled page text for known technology keywords.
    Returns a TechnologyStack with matched technologies per category.
    """
    result: Dict[str, List[str]] = {cat: [] for cat in TECH_PATTERNS}

    for category, keywords in TECH_PATTERNS.items():
        for keyword in keywords:
            # Word-boundary safe match (case-insensitive)
            pattern = re.compile(r"\b" + re.escape(keyword) + r"\b", re.IGNORECASE)
            if pattern.search(all_text):
                if keyword not in result[category]:
                    result[category].append(keyword)

    stack = TechnologyStack(**result)
    logger.info(f"Technologies detected: { {k: v for k, v in result.items() if v} }")
    return stack


# ---------------------------------------------------------------------------
# 5. News Collection
# ---------------------------------------------------------------------------

def get_company_news(domain: str) -> List[Dict[str, Any]]:
    """
    Retrieve recent company news.

    Currently returns mock structured data.
    -------------------------------------------------------------------------
    PRODUCTION UPGRADE: Replace the body of this function with a real API:
      from langchain_community.tools.tavily_search import TavilySearchResults
      tool = TavilySearchResults(max_results=5)
      results = tool.invoke(f"site:{domain} OR {company_name} news funding product launch 2024 2025")
    -------------------------------------------------------------------------
    """
    logger.info(f"Fetching news for domain: {domain}")
    # Mock: returns empty list. Wire to Tavily/Bing to get live results.
    return []


# ---------------------------------------------------------------------------
# 6. Context Merger
# ---------------------------------------------------------------------------

def merge_research_context(
    pages: Dict[str, str],
    metadata: Dict[str, Any],
    tech_stack: TechnologyStack,
    news: List[Dict[str, Any]],
) -> str:
    """
    Merge all collected data sources into a single structured text block
    to be sent to the LLM for Stage 1 fact extraction.
    """
    sections = []

    # Metadata section
    if metadata:
        meta_text = "\n".join(
            f"  {k}: {v}" for k, v in metadata.items()
            if v and k != "social_links"
        )
        sections.append(f"=== METADATA ===\n{meta_text}")

    # Social links
    social = metadata.get("social_links", {})
    if any(social.values()):
        links_text = "\n".join(f"  {k}: {v}" for k, v in social.items() if v)
        sections.append(f"=== SOCIAL LINKS ===\n{links_text}")

    # Technology signals
    tech_dict = {k: v for k, v in tech_stack.model_dump().items() if v}
    if tech_dict:
        tech_text = "\n".join(f"  {cat}: {', '.join(items)}" for cat, items in tech_dict.items())
        sections.append(f"=== TECHNOLOGY SIGNALS ===\n{tech_text}")

    # Page content
    for page_name, content in pages.items():
        sections.append(f"=== PAGE: {page_name.upper()} ===\n{content}")

    # News
    if news:
        news_text = json.dumps(news, indent=2)
        sections.append(f"=== RECENT NEWS ===\n{news_text}")

    return "\n\n".join(sections)
