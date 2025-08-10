"""OpenAI SDK conversation runner."""

import json
from typing import Any

from openai import AsyncOpenAI

from meccaai.adapters.openai_sdk.tool_adapter import (
    tools_to_openai_functions,
)
from meccaai.core.config import settings
from meccaai.core.logging import get_logger
from meccaai.core.tool_registry import get_registry
from meccaai.core.types import Message, Tool, ToolResult

logger = get_logger(__name__)


class OpenAIRunner:
    """OpenAI conversation runner with tool support."""

    def __init__(self, api_key: str | None = None):
        self.client = AsyncOpenAI(api_key=api_key or settings.openai_api_key)
        self.registry = get_registry()

    async def run_conversation(
        self,
        messages: list[Message],
        tools: list[Tool] | None = None,
        model: str | None = None,
    ) -> Message:
        """Run a conversation with optional tool support."""
        # Use provided tools or get all registered tools
        available_tools = tools or self.registry.list_tools()

        # Convert messages to OpenAI format
        openai_messages = [self._message_to_openai(msg) for msg in messages]

        # Convert tools to OpenAI format
        openai_tools = None
        if available_tools:
            openai_tools = tools_to_openai_functions(available_tools)

        # Get model configuration
        model_name = model or settings.models.openai.model

        try:
            # Call OpenAI API
            response = await self.client.chat.completions.create(
                model=model_name,
                messages=openai_messages,
                tools=openai_tools,
                temperature=settings.models.openai.temperature,
                max_tokens=settings.models.openai.max_tokens,
            )

            message = response.choices[0].message

            # Handle tool calls if present
            if message.tool_calls:
                # Execute tool calls
                tool_results = []
                for tool_call in message.tool_calls:
                    result = await self._execute_tool_call(tool_call, available_tools)
                    tool_results.append(result)

                # Add tool call results to conversation
                openai_messages.append(message)
                for result in tool_results:
                    # Safely serialize the result
                    if result.success and result.result is not None:
                        try:
                            content = json.dumps(result.result, default=str)
                        except (TypeError, ValueError):
                            content = str(result.result)
                    else:
                        content = result.error or "Tool execution failed"

                    openai_messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": result.id or "unknown",
                            "content": content,
                        }
                    )

                # Get final response
                final_response = await self.client.chat.completions.create(
                    model=model_name,
                    messages=openai_messages,
                    temperature=settings.models.openai.temperature,
                    max_tokens=settings.models.openai.max_tokens,
                )

                final_message = final_response.choices[0].message
                return Message(
                    role="assistant",
                    content=final_message.content or "",
                )

            return Message(
                role="assistant",
                content=message.content or "",
            )

        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return Message(
                role="assistant",
                content=f"Error: {str(e)}",
            )

    async def _execute_tool_call(
        self,
        tool_call: Any,
        available_tools: list[Tool],
    ) -> ToolResult:
        """Execute a single tool call."""
        try:
            # Find the tool
            tool = None
            for t in available_tools:
                if t.name == tool_call.function.name:
                    tool = t
                    break

            if not tool:
                return ToolResult(
                    id=tool_call.id,
                    success=False,
                    result=None,
                    error=f"Tool not found: {tool_call.function.name}",
                )

            # Parse arguments
            try:
                arguments = json.loads(tool_call.function.arguments)
            except json.JSONDecodeError as e:
                return ToolResult(
                    id=tool_call.id,
                    success=False,
                    result=None,
                    error=f"Invalid arguments JSON: {e}",
                )

            # Execute tool
            result = await tool.call(**arguments)
            result.id = tool_call.id
            return result

        except Exception as e:
            return ToolResult(
                id=tool_call.id,
                success=False,
                result=None,
                error=str(e),
            )

    def _message_to_openai(self, message: Message) -> dict[str, Any]:
        """Convert Message to OpenAI message format."""
        return {
            "role": message.role,
            "content": message.content,
        }
