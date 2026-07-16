"""
parser.py — Output parsing and Pydantic validation for the Company Fit Agent.

Three-tier fallback strategy ensures the pipeline never crashes from a malformed LLM response.
"""
import json
import logging
from typing import Optional, Type, TypeVar

from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel

from .schemas import CompanyFit

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


def get_company_fit_parser() -> PydanticOutputParser:
    """Returns the PydanticOutputParser configured for CompanyFit."""
    return PydanticOutputParser(pydantic_object=CompanyFit)


def parse_company_fit_with_fallback(
    raw_output: str,
    parser: PydanticOutputParser,
    model_class: Type[T] = CompanyFit,
) -> Optional[T]:
    """
    Parse raw LLM output into a CompanyFit model with three fallback tiers.

    Tier 1: Standard PydanticOutputParser (handles format_instructions wrapper).
    Tier 2: Strip markdown code fences, then parse JSON directly.
    Tier 3: Find first { ... } block in the output and parse that.

    Returns:
        Validated CompanyFit instance, or None if all tiers fail.
    """
    # --- Tier 1 ---
    try:
        return parser.parse(raw_output)
    except Exception as e:
        logger.warning(f"[Tier 1] PydanticOutputParser failed: {e}")

    # --- Tier 2 ---
    try:
        cleaned = raw_output.strip()
        if cleaned.startswith("```"):
            parts = cleaned.split("```")
            cleaned = parts[1] if len(parts) > 1 else cleaned
            if cleaned.startswith("json"):
                cleaned = cleaned[4:]
            cleaned = cleaned.strip()
        data = json.loads(cleaned)
        return model_class.model_validate(data)
    except Exception as e:
        logger.warning(f"[Tier 2] Markdown-stripped JSON parse failed: {e}")

    # --- Tier 3 ---
    try:
        start = raw_output.find("{")
        end   = raw_output.rfind("}") + 1
        if start != -1 and end > start:
            data = json.loads(raw_output[start:end])
            return model_class.model_validate(data)
    except Exception as e:
        logger.error(f"[Tier 3] Substring JSON extraction failed: {e}")
        logger.debug(f"Raw output snippet:\n{raw_output[:500]}")

    return None
