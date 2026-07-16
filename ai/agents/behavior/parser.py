"""
parser.py — Output parsing and validation for the Intent Analysis Agent.

Provides the PydanticOutputParser for BehaviorAnalysis and a
fallback-safe parse utility to avoid pipeline crashes on malformed LLM output.
"""
import json
import logging
from typing import Optional, TypeVar, Type

from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel

from .schemas import BehaviorAnalysis

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


def get_behavior_parser() -> PydanticOutputParser:
    """
    Returns the PydanticOutputParser configured for BehaviorAnalysis.
    """
    return PydanticOutputParser(pydantic_object=BehaviorAnalysis)


def parse_behavior_with_fallback(
    raw_output: str,
    parser: PydanticOutputParser,
    model_class: Type[T] = BehaviorAnalysis,
) -> Optional[T]:
    """
    Parse the raw LLM output string into a BehaviorAnalysis model.

    Strategy:
    1. Try PydanticOutputParser directly (handles format_instructions wrapper).
    2. Strip markdown code fences and retry raw JSON parse.
    3. Attempt partial field extraction from JSON if top-level keys exist.
    4. Log error and return None — caller handles graceful fallback.

    Args:
        raw_output: Raw string from the LLM.
        parser: PydanticOutputParser instance.
        model_class: Target Pydantic model class.

    Returns:
        Validated model instance or None.
    """
    # --- Attempt 1: Standard PydanticOutputParser ---
    try:
        return parser.parse(raw_output)
    except Exception as e:
        logger.warning(f"Primary behavior parser failed: {e}. Attempting JSON fallback.")

    # --- Attempt 2: Strip markdown fences ---
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
        logger.warning(f"Markdown-stripped JSON parse failed: {e}. Attempting partial extraction.")

    # --- Attempt 3: Find JSON object within text ---
    try:
        start = raw_output.find("{")
        end = raw_output.rfind("}") + 1
        if start != -1 and end > start:
            json_str = raw_output[start:end]
            data = json.loads(json_str)
            return model_class.model_validate(data)
    except Exception as e:
        logger.error(f"Partial JSON extraction also failed: {e}")
        logger.debug(f"Raw LLM output:\n{raw_output[:600]}")

    return None
