"""Comprehensive conversation logger for tracking user interactions, responses, and tool calls."""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from meccaai.core.logging import get_logger
from meccaai.core.types import Message, ToolResult

logger = get_logger(__name__)


class ConversationLogger:
    """Logger for tracking complete conversation sessions with tool calls."""
    
    def __init__(self, log_dir: str = "logs"):
        """Initialize conversation logger."""
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Create conversation log file with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = self.log_dir / f"conversation_{timestamp}.jsonl"
        
        # Current session tracking
        self.session_id = str(uuid.uuid4())
        self.conversation_count = 0
        
        logger.info(f"📝 Conversation logging initialized: {self.log_file}")
    
    def log_conversation_start(self, user_message: str, model: str, agent: str | None = None):
        """Log the start of a new conversation."""
        self.conversation_count += 1
        self.current_conversation_id = str(uuid.uuid4())
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "conversation_id": self.current_conversation_id,
            "conversation_number": self.conversation_count,
            "event_type": "conversation_start",
            "user_message": user_message,
            "model": model,
            "agent": agent,
            "tools_called": [],
            "ai_response": None,
            "status": "started",
            "metadata": {
                "user_message_length": len(user_message),
                "timestamp_utc": datetime.utcnow().isoformat()
            }
        }
        
        self._write_log(log_entry)
        self.current_log_entry = log_entry
        
        logger.info(f"🎯 Started conversation {self.conversation_count}: {user_message[:50]}...")
    
    def log_tool_call(self, tool_name: str, tool_input: dict[str, Any], tool_result: ToolResult):
        """Log a tool call and its result."""
        tool_call_entry = {
            "timestamp": datetime.now().isoformat(),
            "tool_name": tool_name,
            "tool_input": self._serialize_for_json(tool_input),
            "tool_result": {
                "success": tool_result.success,
                "result": self._serialize_for_json(tool_result.result),
                "error": tool_result.error,
                "id": tool_result.id
            },
            "execution_time": None  # Could be added if we track timing
        }
        
        # Add to current conversation's tool calls
        if hasattr(self, 'current_log_entry'):
            self.current_log_entry["tools_called"].append(tool_call_entry)
        
        logger.info(f"🔧 Tool called: {tool_name} - {'✅ Success' if tool_result.success else '❌ Failed'}")
    
    def log_ai_response(self, ai_response: str):
        """Log the AI's final response."""
        if hasattr(self, 'current_log_entry'):
            self.current_log_entry["ai_response"] = ai_response
            self.current_log_entry["status"] = "completed"
            self.current_log_entry["metadata"].update({
                "ai_response_length": len(ai_response),
                "total_tools_used": len(self.current_log_entry["tools_called"]),
                "completion_timestamp": datetime.now().isoformat()
            })
            
            # Write the completed conversation
            self._write_log(self.current_log_entry)
            
            logger.info(f"💬 AI response logged ({len(ai_response)} chars, {len(self.current_log_entry['tools_called'])} tools)")
    
    def log_error(self, error: str):
        """Log an error that occurred during conversation."""
        if hasattr(self, 'current_log_entry'):
            self.current_log_entry["status"] = "error"
            self.current_log_entry["error"] = error
            self.current_log_entry["metadata"]["error_timestamp"] = datetime.now().isoformat()
            
            self._write_log(self.current_log_entry)
            
            logger.error(f"❌ Conversation error logged: {error}")
    
    def _serialize_for_json(self, obj: Any) -> Any:
        """Serialize complex objects for JSON logging."""
        if obj is None:
            return None
        elif isinstance(obj, (str, int, float, bool)):
            return obj
        elif isinstance(obj, dict):
            return {k: self._serialize_for_json(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [self._serialize_for_json(item) for item in obj]
        elif hasattr(obj, '__dict__'):
            # Handle objects with __dict__ (like custom classes)
            return self._serialize_for_json(obj.__dict__)
        else:
            # Fallback: convert to string
            return str(obj)
    
    def _write_log(self, log_entry: dict[str, Any]):
        """Write log entry to JSONL file."""
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
        except Exception as e:
            logger.error(f"Failed to write conversation log: {e}")
    
    def get_conversation_stats(self) -> dict[str, Any]:
        """Get statistics about the current session."""
        return {
            "session_id": self.session_id,
            "total_conversations": self.conversation_count,
            "log_file": str(self.log_file),
            "session_start": datetime.now().isoformat()  # This should be tracked from init
        }


# Global conversation logger instance
_conversation_logger = None


def get_conversation_logger() -> ConversationLogger:
    """Get or create the global conversation logger."""
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