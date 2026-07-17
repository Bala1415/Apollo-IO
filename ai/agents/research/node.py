"""
node.py — LangGraph node for the Research Agent.

Orchestrates the unified Company Intelligence pipeline:
  1. Check Cache
  2. Crawl and parse
  3. Extract metadata, tech stack, news
  4. Unified LLM Call -> CompanyResearch
  5. Save to Cache
"""
import logging
import time
from typing import Dict, Any

from langchain_core.runnables import RunnableConfig

from .tools import (
    discover_website,
    crawl_website,
    extract_metadata,
    detect_technologies,
    get_company_news,
    merge_research_context,
    _fetch_page,
)
from .prompt import get_unified_research_prompt
from .parser import get_research_parser, parse_with_fallback
from .schemas import CompanyResearch
from ai.services.llm_service import llm_service
from ai.services.cache_service import cache_service

logger = logging.getLogger(__name__)

def research_node(state: Dict[str, Any], config: RunnableConfig = None) -> Dict[str, Any]:
    start_time = time.time()
    logger.info("=" * 60)
    logger.info("Research Agent (Unified) — Starting pipeline")

    company_domain: str = state.get("company_domain", "").strip()
    if not company_domain:
        return {"research": {}}

    # 1. Check Cache
    cached_research = cache_service.get_research(company_domain)
    if cached_research:
        logger.info(f"Research Cache hit for {company_domain}")
        return {"research": cached_research}

    # 2. Discover website
    base_url = discover_website(company_domain)
    logger.info(f"Resolved website: {base_url}")

    # 3. Crawl multiple pages
    pages = {}
    try:
        pages = crawl_website(base_url)
    except Exception as e:
        logger.error(f"Website crawl failed: {e}")

    # 4. Extract metadata
    metadata = {}
    try:
        homepage_html = _fetch_page(base_url)
        if homepage_html:
            metadata = extract_metadata(homepage_html, base_url)
    except Exception as e:
        logger.warning(f"Metadata extraction failed: {e}")

    # 5. Detect technologies
    from .schemas import TechnologyStack
    tech_stack = TechnologyStack()
    try:
        all_text = " ".join(pages.values())
        if all_text:
            tech_stack = detect_technologies(all_text)
    except Exception as e:
        logger.warning(f"Technology detection failed: {e}")

    # 6. Collect company news
    news = []
    try:
        news = get_company_news(company_domain)
    except Exception as e:
        logger.warning(f"News collection failed: {e}")

    # 7. Merge all context
    merged_context = merge_research_context(pages, metadata, tech_stack, news)

    if not merged_context.strip():
        return {"research": {}}

    # 8. Unified LLM Call
    parser = get_research_parser()
    prompt = get_unified_research_prompt()
    chain = prompt | llm_service._client

    final_result = None
    try:
        raw = llm_service.invoke(
            chain,
            {
                "company_domain": company_domain,
                "merged_context": merged_context,
                "format_instructions": parser.get_format_instructions(),
            },
        )
        text = raw.content if hasattr(raw, "content") else str(raw)
        final_result = parse_with_fallback(text, parser, CompanyResearch)
    except Exception as e:
        logger.error(f"Unified LLM failed: {e}")

    if final_result:
        output = final_result.model_dump()
        output.setdefault("sources", [])
        crawled_urls = [f"{base_url}/{p}" if p != "home" else base_url for p in pages.keys()]
        if isinstance(output.get("sources"), list):
            output["sources"] = list(set((output["sources"] or []) + crawled_urls))
            
        # Save to cache
        cache_service.set_research(company_domain, output)
        return {"research": output}

    return {"research": {}}
