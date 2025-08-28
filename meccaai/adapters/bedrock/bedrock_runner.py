"""AWS Bedrock conversation runner."""

import json
from typing import Any

import boto3
from botocore.exceptions import ClientError

from meccaai.core.config import get_settings
from meccaai.core.loggers import ai_logger
from meccaai.core.logging import get_logger
from meccaai.core.tool_registry import get_registry
from meccaai.core.types import Message, Tool, ToolResult

logger = get_logger(__name__)


class BedrockRunner:
    """AWS Bedrock conversation runner with tool support."""

    def __init__(self, region_name: str | None = None):
        """Initialize Bedrock runner."""
        # Get fresh settings to ensure we have latest config
        settings = get_settings()
        self.region_name = region_name or settings.aws_region
        self.registry = get_registry()

        # Initialize Bedrock client with explicit credentials
        if not settings.aws_access_key_id or not settings.aws_secret_access_key:
            raise ValueError(
                "AWS credentials not found in settings. Please check your .env file."
            )

        session = boto3.Session(
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            region_name=self.region_name,
        )
        self.client = session.client("bedrock-runtime")

    async def run_conversation(
        self,
        messages: list[Message],
        tools: list[Tool] | None = None,
        model: str | None = None,
        agent: str | None = None,
    ) -> Message:
        """Run a conversation with optional tool support."""
        # Use provided tools or get all registered tools
        available_tools = tools or self.registry.list_tools()

        # Convert messages to Bedrock format
        bedrock_messages = [self._message_to_bedrock(msg) for msg in messages]

        # Get model configuration
        settings = get_settings()
        model_name = model or settings.models.bedrock.model

        # Log conversation start
        user_message = messages[-1].content if messages else ""
        ai_logger.log_system_event(
            event_type="bedrock_conversation_start",
            message=f"Starting Bedrock conversation with {agent}",
            data={
                "user_message": user_message,
                "model_name": model_name,
                "agent": agent,
                "available_tools": len(available_tools) if available_tools else 0
            }
        )

        try:
            # Prepare tool schema for Bedrock
            tool_config = None
            if available_tools:
                tool_config = {
                    "tools": self._tools_to_bedrock_schema(available_tools),
                    "tool_choice": {"type": "auto"},
                }

            # Multi-turn conversation loop to handle multiple tool calls
            max_turns = 10  # Prevent infinite loops
            current_messages = bedrock_messages.copy()

            for turn in range(max_turns):
                # Call Bedrock API
                request_body = {
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": settings.models.bedrock.max_tokens,
                    "temperature": settings.models.bedrock.temperature,
                    "messages": current_messages,
                }

                if tool_config:
                    request_body["tools"] = tool_config["tools"]
                    request_body["tool_choice"] = tool_config["tool_choice"]

                logger.info(f"🤖 Calling Bedrock model (turn {turn + 1}): {model_name}")
                logger.debug(f"Request body: {json.dumps(request_body, indent=2)}")

                response = self.client.invoke_model(
                    modelId=model_name,
                    body=json.dumps(request_body),
                    contentType="application/json",
                    accept="application/json",
                )

                # Parse response
                response_body = json.loads(response["body"].read().decode("utf-8"))

                # Handle tool calls if present
                if response_body.get("stop_reason") == "tool_use":
                    content = response_body.get("content", [])
                    tool_results = []

                    # Add assistant response to conversation
                    current_messages.append(
                        {
                            "role": "assistant",
                            "content": content,
                        }
                    )

                    for item in content:
                        if item.get("type") == "tool_use":
                            result = await self._execute_tool_call(
                                item, available_tools
                            )
                            tool_results.append(result)

                    # Add tool results to conversation
                    for result in tool_results:
                        content_data = (
                            result.result
                            if result.success and result.result is not None
                            else result.error or "Tool execution failed"
                        )

                        current_messages.append(
                            {
                                "role": "user",
                                "content": [
                                    {
                                        "type": "tool_result",
                                        "tool_use_id": result.id or "unknown",
                                        "content": str(content_data),
                                    }
                                ],
                            }
                        )

                    # Continue the loop to allow more tool calls
                    continue

                else:
                    # No more tool calls, extract final response
                    content = self._extract_text_content(
                        response_body.get("content", [])
                    )

                    # Log AI response (will be captured by main system)

                    return Message(role="assistant", content=content)

            # If we hit max_turns, return what we have
            logger.warning(f"Hit maximum turns ({max_turns}) in conversation")
            final_content = "I've reached the maximum number of steps for this conversation. Please ask your question again for a fresh start."
            # Log will be handled by main system
            return Message(role="assistant", content=final_content)

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_message = e.response["Error"]["Message"]
            error_text = f"Bedrock API error: {error_code} - {error_message}"
            logger.error(error_text)

            # Log conversation error
            ai_logger.log_system_event(
                event_type="bedrock_conversation_error",
                message="Bedrock API error occurred",
                level="ERROR",
                data={"error": error_text, "error_code": error_code}
            )

            return Message(
                role="assistant",
                content=f"Error: {error_code} - {error_message}",
            )
        except Exception as e:
            error_text = f"Bedrock API error: {str(e)}"
            logger.error(error_text)

            # Log conversation error
            ai_logger.log_system_event(
                event_type="bedrock_conversation_error", 
                message="Bedrock API error occurred",
                level="ERROR",
                data={"error": error_text}
            )

            return Message(
                role="assistant",
                content=f"Error: {str(e)}",
            )

    async def _execute_tool_call(
        self,
        tool_call: dict[str, Any],
        available_tools: list[Tool],
    ) -> ToolResult:
        """Execute a single tool call."""
        try:
            tool_name = tool_call.get("name")
            tool_id = tool_call.get("id")
            tool_input = tool_call.get("input", {})

            # Find the tool
            tool = None
            for t in available_tools:
                if t.name == tool_name:
                    tool = t
                    break

            if not tool:
                return ToolResult(
                    id=tool_id,
                    success=False,
                    result=None,
                    error=f"Tool not found: {tool_name}",
                )

            # Execute tool
            result = await tool.call(**tool_input)
            result.id = tool_id

            # Log tool call and result
            ai_logger.log_tool_execution(
                tool_name=tool_name,
                tool_input=tool_input,
                tool_output=result.result,
                execution_time_ms=0,  # Not tracked here
                success=result.success,
                error=result.error
            )

            return result

        except Exception as e:
            return ToolResult(
                id=tool_call.get("id"),
                success=False,
                result=None,
                error=str(e),
            )

    def _message_to_bedrock(self, message: Message) -> dict[str, Any]:
        """Convert Message to Bedrock message format."""
        # Bedrock only supports 'user' and 'assistant' roles
        role = message.role
        if role == "system":
            # Convert system messages to user messages with special formatting
            role = "user"
            content = f"System: {message.content}"
        else:
            content = message.content

        return {
            "role": role,
            "content": content,
        }

    def _tools_to_bedrock_schema(self, tools: list[Tool]) -> list[dict[str, Any]]:
        """Convert tools to Bedrock tool schema."""
        bedrock_tools = []
        for tool in tools:
            bedrock_tools.append(
                {
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": tool.parameters
                    or {"type": "object", "properties": {}},
                }
            )
        return bedrock_tools

    def _extract_text_content(self, content: list[dict[str, Any]]) -> str:
        """Extract text content from Bedrock response content."""
        text_parts = []
        for item in content:
            if item.get("type") == "text":
                text_parts.append(item.get("text", ""))
        return "".join(text_parts)
