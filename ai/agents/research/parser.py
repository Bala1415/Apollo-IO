"""
parser.py — Two-stage output parsers for the Research Agent.

Stage 1: FactExtractionResult parser
Stage 2: CompanyResearch parser

Both parsers include fallback handling to avoid crashing the pipeline
on malformed LLM output.
"""
import json
import logging
from typing import Optional, TypeVar, Type

from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel

from .schemas import FactExtractionResult, CompanyResearch

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)

# ---------------------------------------------------------------------------
# Parser factories
# ---------------------------------------------------------------------------

def get_fact_extraction_parser() -> PydanticOutputParser:
    """
    Returns the PydanticOutputParser for Stage 1 (Fact Extraction).
    Validates LLM output against FactExtractionResult schema.
    """
    return PydanticOutputParser(pydantic_object=FactExtractionResult)


def get_research_parser() -> PydanticOutputParser:
    """
    Returns the PydanticOutputParser for Stage 2 (Business Reasoning).
    Validates LLM output against the final CompanyResearch schema.
    """
    return PydanticOutputParser(pydantic_object=CompanyResearch)


# ---------------------------------------------------------------------------
# Fallback-safe parsing utility
# ---------------------------------------------------------------------------

def parse_with_fallback(
    raw_output: str,
    parser: PydanticOutputParser,
    model_class: Type[T],
) -> Optional[T]:
    """
    Attempts to parse raw LLM string output using the given Pydantic parser.

    Strategy:
    1. Try the standard PydanticOutputParser (handles format_instructions wrapping).
    2. If that fails, try stripping markdown code fences and parsing raw JSON.
    3. If that fails, log the error and return None (caller handles gracefully).

    Args:
        raw_output: The raw string output from the LLM.
        parser: The PydanticOutputParser to use for primary parsing.
        model_class: The Pydantic model class for fallback direct validation.

    Returns:
        A validated Pydantic model instance, or None on failure.
    """
    # --- Attempt 1: Standard parser ---
    try:
        return parser.parse(raw_output)
    except Exception as e:
        logger.warning(f"Primary parser failed: {e}. Attempting JSON fallback.")

    # --- Attempt 2: Strip markdown fences + direct JSON parse ---
    try:
        # Remove ```json ... ``` or ``` ... ``` wrappers
        cleaned = raw_output.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("```")[1]
            if cleaned.startswith("json"):
                cleaned = cleaned[4:]
            cleaned = cleaned.strip()
        data = json.loads(cleaned)
        return model_class.model_validate(data)
    except Exception as e:
        logger.error(f"Fallback JSON parse also failed: {e}")
        logger.debug(f"Raw LLM output was:\n{raw_output[:500]}")

    return None
