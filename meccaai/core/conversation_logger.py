"""CloudWatch-only conversation logger for tracking user interactions, responses, and tool calls."""

import uuid
from datetime import datetime
from typing import Any

from meccaai.core.logging import get_logger
from meccaai.core.types import ToolResult

# Import CloudWatch logger
try:
    from meccaai.core.cloudwatch_logger import cloudwatch_logger
    CLOUDWATCH_AVAILABLE = True
except ImportError:
    CLOUDWATCH_AVAILABLE = False
    cloudwatch_logger = None

logger = get_logger(__name__)


class ConversationLogger:
    """CloudWatch-only logger for tracking conversation sessions with tool calls."""

    def __init__(self):
        """Initialize CloudWatch-only conversation logger."""
        # Current session tracking
        self.session_id = str(uuid.uuid4())
        self.conversation_count = 0

        if CLOUDWATCH_AVAILABLE and cloudwatch_logger and cloudwatch_logger.enabled:
            logger.info(f"📝 CloudWatch conversation logging initialized (session: {self.session_id[:8]})")
        else:
            logger.warning("⚠️  CloudWatch logging not available")

    def log_conversation_start(
        self, user_message: str, model: str, agent: str | None = None
    ):
        """Log the start of a new conversation."""
        self.conversation_count += 1
        self.current_conversation_id = str(uuid.uuid4())

        # Store conversation metadata for CloudWatch logging
        self.current_log_entry = {
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "conversation_id": self.current_conversation_id,
            "conversation_number": self.conversation_count,
            "user_message": user_message,
            "model": model,
            "agent": agent,
            "tools_called": [],
            "status": "in_progress",
            "metadata": {
                "user_message_length": len(user_message),
                "start_timestamp": datetime.now().isoformat(),
            },
        }

        logger.info(
            f"🚀 Started conversation #{self.conversation_count} "
            f"({len(user_message)} chars, model: {model}, agent: {agent or 'none'})"
        )

    def log_tool_call(
        self, tool_name: str, tool_input: dict[str, Any], tool_result: ToolResult
    ):
        """Log a tool call and its result."""
        tool_call_entry = {
            "timestamp": datetime.now().isoformat(),
            "tool_name": tool_name,
            "tool_input": tool_input,
            "tool_result": {
                "success": tool_result.success,
                "result": str(tool_result.result)[:500] if tool_result.result else None,  # Truncate large results
                "error": tool_result.error,
                "id": tool_result.id,
            },
            "execution_time_ms": 0,  # Default value
        }

        # Add to current conversation's tool calls
        if hasattr(self, "current_log_entry"):
            self.current_log_entry["tools_called"].append(tool_call_entry)

        # Log tool execution to CloudWatch if available
        if CLOUDWATCH_AVAILABLE and cloudwatch_logger:
            try:
                cloudwatch_logger.log_tool_execution(
                    tool_name=tool_name,
                    tool_input=tool_input,
                    tool_output=tool_result.result,
                    execution_time_ms=tool_call_entry.get("execution_time_ms", 0),
                    success=tool_result.success,
                    error=tool_result.error
                )
            except Exception as e:
                logger.warning(f"Failed to log tool execution to CloudWatch: {e}")

        logger.info(
            f"🔧 Tool called: {tool_name} - {'✅ Success' if tool_result.success else '❌ Failed'}"
        )

    def log_ai_response(self, ai_response: str):
        """Log the AI's final response to CloudWatch only."""
        if hasattr(self, "current_log_entry"):
            self.current_log_entry["ai_response"] = ai_response
            self.current_log_entry["status"] = "completed"
            self.current_log_entry["metadata"].update(
                {
                    "ai_response_length": len(ai_response),
                    "total_tools_used": len(self.current_log_entry["tools_called"]),
                    "completion_timestamp": datetime.now().isoformat(),
                }
            )

            # Send to CloudWatch if available
            if CLOUDWATCH_AVAILABLE and cloudwatch_logger:
                try:
                    # Extract data for CloudWatch logging
                    start_time = datetime.fromisoformat(self.current_log_entry["timestamp"])
                    end_time = datetime.fromisoformat(self.current_log_entry["metadata"]["completion_timestamp"])
                    execution_time_ms = int((end_time - start_time).total_seconds() * 1000)

                    # Extract tool calls for CloudWatch
                    tool_calls = [
                        {
                            "tool_name": call["tool_name"],
                            "success": call["tool_result"]["success"],
                            "execution_time_ms": call.get("execution_time_ms", 0)
                        }
                        for call in self.current_log_entry["tools_called"]
                    ]

                    cloudwatch_logger.log_ai_response(
                        user_query=self.current_log_entry["user_message"],
                        ai_response=ai_response,
                        tool_calls=tool_calls,
                        execution_time_ms=execution_time_ms,
                        model_name=self.current_log_entry.get("model", "unknown"),
                        error=None,
                        metadata={
                            "agent": self.current_log_entry.get("agent"),
                            "session_id": self.current_log_entry.get("session_id"),
                            "conversation_id": self.current_log_entry.get("conversation_id"),
                            "total_tools_used": len(tool_calls),
                            "ai_response_length": len(ai_response)
                        }
                    )
                except Exception as e:
                    logger.warning(f"Failed to log to CloudWatch: {e}")

            logger.info(
                f"💬 AI response logged to CloudWatch ({len(ai_response)} chars, {len(self.current_log_entry['tools_called'])} tools)"
            )

    def log_error(self, error: str):
        """Log an error that occurred during conversation to CloudWatch only."""
        if hasattr(self, "current_log_entry"):
            self.current_log_entry["status"] = "error"
            self.current_log_entry["error"] = error
            self.current_log_entry["metadata"]["error_timestamp"] = (
                datetime.now().isoformat()
            )

            # Log error to CloudWatch if available
            if CLOUDWATCH_AVAILABLE and cloudwatch_logger:
                try:
                    # Calculate execution time if available
                    start_time = datetime.fromisoformat(self.current_log_entry["timestamp"])
                    error_time = datetime.fromisoformat(self.current_log_entry["metadata"]["error_timestamp"])
                    execution_time_ms = int((error_time - start_time).total_seconds() * 1000)

                    cloudwatch_logger.log_ai_response(
                        user_query=self.current_log_entry["user_message"],
                        ai_response=None,
                        tool_calls=[],
                        execution_time_ms=execution_time_ms,
                        model_name=self.current_log_entry.get("model", "unknown"),
                        error=error,
                        metadata={
                            "agent": self.current_log_entry.get("agent"),
                            "session_id": self.current_log_entry.get("session_id"),
                            "conversation_id": self.current_log_entry.get("conversation_id"),
                            "error": True
                        }
                    )
                except Exception as e:
                    logger.warning(f"Failed to log error to CloudWatch: {e}")

            logger.error(f"❌ Conversation error logged to CloudWatch: {error}")


# Global instance for easy access
_conversation_logger = None


def get_conversation_logger() -> ConversationLogger:
    """Get the global conversation logger instance."""
    global _conversation_logger
    if _conversation_logger is None:
        _conversation_logger = ConversationLogger()
    return _conversation_logger


def log_conversation_start(user_message: str, model: str, agent: str | None = None):
    """Convenience function to log conversation start."""
    get_conversation_logger().log_conversation_start(user_message, model, agent)


def log_tool_call(tool_name: str, tool_input: dict[str, Any], tool_result: ToolResult):
    """Convenience function to log tool call."""
    get_conversation_logger().log_tool_call(tool_name, tool_input, tool_result)


def log_ai_response(ai_response: str):
    """Convenience function to log AI response."""
    get_conversation_logger().log_ai_response(ai_response)


def log_conversation_error(error: str):
    """Convenience function to log conversation error."""
    get_conversation_logger().log_error(error)
