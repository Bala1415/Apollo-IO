"""servicesAction

This module provides a simple “action prompt” implementation:

- Purpose: Explain selected code or a concept in simple terms.
- Input: Typically the active editor content, or a provided file/terminal/code block.
- Output: A plain-language explanation covering purpose and logic.

Note:
This repository may integrate actions into a larger agent/graph system.
In that case, this file can be imported and called by the action runner.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class ExplainRequest:
    """Represents a request to explain code or a concept."""

    instruction: str = (
        "Explain the selected code or concept in simple terms. "
        "If a specific file, terminal output, or code block is provided, use that instead."
    )
    file_path: Optional[str] = None
    code_block: Optional[str] = None
    terminal_output: Optional[str] = None


def build_explanation_prompt(req: ExplainRequest) -> str:
    """Build a text prompt for an LLM/agent from the provided request."""

    parts: list[str] = [req.instruction]

    if req.file_path:
        parts.append(f"File path: {req.file_path}")

    if req.code_block:
        parts.append("Code block:\n" + req.code_block)

    if req.terminal_output:
        parts.append("Terminal output:\n" + req.terminal_output)

    return "\n\n".join(parts)


def explain_selected_code(req: ExplainRequest) -> str:
    """Return the prompt text that an upstream agent can use.

    This function does not call an LLM directly; it just prepares the prompt.
    """

    return build_explanation_prompt(req)

