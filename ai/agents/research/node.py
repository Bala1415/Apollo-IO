"""
node.py — LangGraph node for the Research Agent.

Orchestrates the full two-stage Company Intelligence pipeline:

  1.  Read company_domain from GraphState
  2.  Discover website URL
  3.  Crawl multiple pages concurrently
  4.  Extract structured metadata from homepage
  5.  Detect technology stack from all page text
  6.  Collect company news
  7.  Merge all context into a unified text block
  8.  Stage 1 LLM — Fact Extraction
  9.  Stage 2 LLM — Business Reasoning
  10. Validate final output with Pydantic
  11. Update GraphState["research"]
  12. Return updated state

Only state["research"] is modified. All other state keys are untouched.
"""
import logging
import time
from typing import Dict, Any

from langchain_groq import ChatGroq
from langchain_core.runnables import RunnableConfig
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from .tools import (
    discover_website,
    crawl_website,
    extract_metadata,
    detect_technologies,
    get_company_news,
    merge_research_context,
    _fetch_page,
)
from .prompt import get_fact_extraction_prompt, get_business_reasoning_prompt
from .parser import get_fact_extraction_parser, get_research_parser, parse_with_fallback
from .schemas import CompanyResearch, FactExtractionResult

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# LLM factory — swap model here if needed
# ---------------------------------------------------------------------------

def _build_llm() -> ChatGroq:
    """
    Instantiates the LLM used by the Research Agent.
    Inject via dependency injection or environment variable for production.
    """
    return ChatGroq(model="llama-3.3-70b-versatile", temperature=0)


# ---------------------------------------------------------------------------
# Retryable LLM invocation
# ---------------------------------------------------------------------------

@retry(
    retry=retry_if_exception_type(Exception),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=30),
    reraise=True,
)
def _invoke_llm_with_retry(chain, inputs: Dict[str, Any]) -> str:
    """
    Invoke an LLM chain with automatic retry on transient failures.
    Returns raw string output from the LLM.
    """
    return chain.invoke(inputs)


# ---------------------------------------------------------------------------
# Main LangGraph node
# ---------------------------------------------------------------------------

def research_node(state: Dict[str, Any], config: RunnableConfig = None) -> Dict[str, Any]:
    """
    LangGraph node — Production-Grade Company Intelligence Engine.

    Reads company_domain from state, runs the full two-stage research pipeline,
    and returns only {"research": <CompanyResearch dict>}.

    Never raises exceptions — always returns a valid dict.
    """
    start_time = time.time()
    logger.info("=" * 60)
    logger.info("Research Agent — Starting pipeline")

    # ------------------------------------------------------------------
    # 0. Validate input
    # ------------------------------------------------------------------
    company_domain: str = state.get("company_domain", "").strip()
    if not company_domain:
        logger.warning("No company_domain provided in state. Returning empty research.")
        return {"research": {}}

    logger.info(f"Domain: {company_domain}")

    # ------------------------------------------------------------------
    # 1. Discover website
    # ------------------------------------------------------------------
    base_url = discover_website(company_domain)
    logger.info(f"Resolved website: {base_url}")

    # ------------------------------------------------------------------
    # 2. Crawl multiple pages
    # ------------------------------------------------------------------
    logger.info("Step 2: Crawling website pages...")
    pages: Dict[str, str] = {}
    try:
        pages = crawl_website(base_url)
    except Exception as e:
        logger.error(f"Website crawl failed: {e}. Proceeding with empty pages.")

    # ------------------------------------------------------------------
    # 3. Extract metadata from homepage
    # ------------------------------------------------------------------
    logger.info("Step 3: Extracting homepage metadata...")
    metadata: Dict[str, Any] = {}
    try:
        homepage_html = _fetch_page(base_url)
        if homepage_html:
            metadata = extract_metadata(homepage_html, base_url)
            logger.info(f"Metadata extracted: {list(metadata.keys())}")
    except Exception as e:
        logger.warning(f"Metadata extraction failed: {e}")

    # ------------------------------------------------------------------
    # 4. Detect technologies from all page text
    # ------------------------------------------------------------------
    logger.info("Step 4: Detecting technology stack...")
    from .schemas import TechnologyStack
    tech_stack = TechnologyStack()
    try:
        all_text = " ".join(pages.values())
        if all_text:
            tech_stack = detect_technologies(all_text)
    except Exception as e:
        logger.warning(f"Technology detection failed: {e}")

    # ------------------------------------------------------------------
    # 5. Collect company news
    # ------------------------------------------------------------------
    logger.info("Step 5: Collecting company news...")
    news = []
    try:
        news = get_company_news(company_domain)
    except Exception as e:
        logger.warning(f"News collection failed: {e}")

    # ------------------------------------------------------------------
    # 6. Merge all context
    # ------------------------------------------------------------------
    logger.info("Step 6: Merging research context...")
    merged_context = merge_research_context(pages, metadata, tech_stack, news)
    logger.info(f"Merged context size: {len(merged_context)} chars")

    if not merged_context.strip():
        logger.error("No content collected. Cannot proceed with LLM. Returning empty research.")
        return {"research": {}}

    # ------------------------------------------------------------------
    # 7. LLM setup
    # ------------------------------------------------------------------
    llm = _build_llm()
    fact_parser = get_fact_extraction_parser()
    research_parser = get_research_parser()
    fact_prompt = get_fact_extraction_prompt()
    reasoning_prompt = get_business_reasoning_prompt()

    # ------------------------------------------------------------------
    # 8. Stage 1 — Fact Extraction
    # ------------------------------------------------------------------
    logger.info("Step 7: Stage 1 LLM — Fact Extraction...")
    extracted_facts: FactExtractionResult | None = None

    try:
        stage1_chain = fact_prompt | llm
        stage1_raw = _invoke_llm_with_retry(
            stage1_chain,
            {
                "company_domain": company_domain,
                "merged_context": merged_context,
                "format_instructions": fact_parser.get_format_instructions(),
            },
        )
        # Handle both AIMessage and str responses
        stage1_text = stage1_raw.content if hasattr(stage1_raw, "content") else str(stage1_raw)
        extracted_facts = parse_with_fallback(stage1_text, fact_parser, FactExtractionResult)

        if extracted_facts:
            logger.info(f"Stage 1 complete — extracted facts for: {extracted_facts.company_name}")
        else:
            logger.warning("Stage 1 parsing returned None. Continuing with raw context fallback.")
    except Exception as e:
        logger.error(f"Stage 1 LLM failed: {e}")

    # ------------------------------------------------------------------
    # 9. Stage 2 — Business Reasoning
    # ------------------------------------------------------------------
    logger.info("Step 8: Stage 2 LLM — Business Reasoning...")

    # Prepare input for stage 2: prefer parsed facts, fall back to raw context
    if extracted_facts:
        facts_text = extracted_facts.model_dump_json(indent=2)
    else:
        logger.warning("No Stage 1 facts available. Stage 2 will use raw merged context.")
        facts_text = merged_context[:6000]  # Safety cap

    final_result: CompanyResearch | None = None

    try:
        stage2_chain = reasoning_prompt | llm
        stage2_raw = _invoke_llm_with_retry(
            stage2_chain,
            {
                "company_domain": company_domain,
                "extracted_facts": facts_text,
                "format_instructions": research_parser.get_format_instructions(),
            },
        )
        stage2_text = stage2_raw.content if hasattr(stage2_raw, "content") else str(stage2_raw)
        final_result = parse_with_fallback(stage2_text, research_parser, CompanyResearch)

        if final_result:
            logger.info(f"Stage 2 complete — executive summary generated: {bool(final_result.executive_summary)}")
        else:
            logger.warning("Stage 2 parsing returned None.")
    except Exception as e:
        logger.error(f"Stage 2 LLM failed: {e}")

    # ------------------------------------------------------------------
    # 10. Build output
    # ------------------------------------------------------------------
    elapsed = round(time.time() - start_time, 2)
    logger.info(f"Research Agent pipeline complete in {elapsed}s")
    logger.info("=" * 60)

    if final_result:
        # Ensure sources always include the crawled page URLs
        output = final_result.model_dump()
        output.setdefault("sources", [])
        crawled_urls = [f"{base_url}/{p}" if p != "home" else base_url for p in pages.keys()]
        if isinstance(output.get("sources"), list):
            output["sources"] = list(set((output["sources"] or []) + crawled_urls))
        return {"research": output}

    # Graceful degradation: return what we got from Stage 1, if anything
    if extracted_facts:
        logger.warning("Returning partial Stage 1 result due to Stage 2 failure.")
        return {
            "research": {
                "company": {
                    "name": extracted_facts.company_name,
                    "website": extracted_facts.website,
                    "description": extracted_facts.description,
                    "founded_year": extracted_facts.founded_year,
                    "headquarters": extracted_facts.headquarters,
                    "employee_count": extracted_facts.employee_count,
                    "funding": extracted_facts.funding,
                },
                "products": [p.model_dump() for p in (extracted_facts.products or [])],
                "services": [s.model_dump() for s in (extracted_facts.services or [])],
                "technology": extracted_facts.technology.model_dump() if extracted_facts.technology else {},
                "sources": list(pages.keys()),
                "executive_summary": None,
            }
        }

    logger.error("Both LLM stages failed. Returning empty research.")
    return {"research": {}}
