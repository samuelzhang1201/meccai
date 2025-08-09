"""OpenAI SDK tool adapter - converts tools to OpenAI format."""

from typing import Any

from meccaai.core.types import Tool


def tool_to_openai_function(tool: Tool) -> dict[str, Any]:
    """Convert a Tool to OpenAI function format."""
    return {
        "type": "function",
        "function": {
            "name": tool.name,
            "description": tool.description,
            "parameters": tool.parameters,
        },
    }


def tools_to_openai_functions(tools: list[Tool]) -> list[dict[str, Any]]:
    """Convert a list of Tools to OpenAI functions format."""
    return [tool_to_openai_function(tool) for tool in tools]


def extract_tool_calls_from_message(message: Any) -> list[dict[str, Any]]:
    """Extract tool calls from an OpenAI message."""
    tool_calls = []

    if hasattr(message, "tool_calls") and message.tool_calls:
        for tool_call in message.tool_calls:
            tool_calls.append(
                {
                    "id": tool_call.id,
                    "name": tool_call.function.name,
                    "arguments": tool_call.function.arguments,
                }
            )

    return tool_calls
