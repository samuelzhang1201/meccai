"""Prompt loader utility for loading prompt files."""

import re
from pathlib import Path
from typing import Any


def load_prompt(prompt_path: str) -> str:
    """Load a prompt from a markdown file.

    Args:
        prompt_path: Relative path to the prompt file (e.g., 'semantic_layer/get_dimensions.md')

    Returns:
        The loaded prompt content as a string
    """
    current_dir = Path(__file__).parent
    full_path = current_dir / prompt_path

    if not full_path.exists():
        raise FileNotFoundError(f"Prompt file not found: {full_path}")

    return full_path.read_text(encoding="utf-8").strip()


def parse_prompt_metadata(prompt_content: str) -> dict[str, Any]:
    """Parse prompt metadata from structured markdown.

    Args:
        prompt_content: The prompt content

    Returns:
        Dictionary containing parsed metadata like instructions, parameters, examples
    """
    metadata = {}

    # Extract instructions
    instructions_match = re.search(
        r"<instructions>(.*?)</instructions>", prompt_content, re.DOTALL
    )
    if instructions_match:
        metadata["instructions"] = instructions_match.group(1).strip()

    # Extract parameters
    parameters_match = re.search(
        r"<parameters>(.*?)</parameters>", prompt_content, re.DOTALL
    )
    if parameters_match:
        metadata["parameters"] = parameters_match.group(1).strip()

    # Extract examples
    examples_match = re.search(r"<examples>(.*?)</examples>", prompt_content, re.DOTALL)
    if examples_match:
        metadata["examples"] = examples_match.group(1).strip()

    # If no structured format, return the whole content as instructions
    if not metadata:
        metadata["instructions"] = prompt_content

    return metadata


def get_tool_description(prompt_path: str) -> str:
    """Get tool description from prompt file.

    Args:
        prompt_path: Relative path to the prompt file

    Returns:
        Tool description suitable for agent instructions
    """
    prompt_content = load_prompt(prompt_path)
    metadata = parse_prompt_metadata(prompt_content)

    # Use instructions as the main description
    return metadata.get("instructions", prompt_content)
