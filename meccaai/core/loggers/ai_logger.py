"""Unified AI logging interface that coordinates local and CloudWatch logging."""

from typing import Any, Dict, Optional
from meccaai.core.loggers.local_logger import local_logger
from meccaai.core.loggers.cloudwatch_logger import cloudwatch_logger


class AILogger:
    """Unified interface for AI interaction logging."""
    
    def __init__(self):
        """Initialize unified logger."""
        self.local = local_logger
        self.cloudwatch = cloudwatch_logger
    
    def log_ai_interaction(
        self,
        user_prompt: str,
        ai_response: str,
        thinking: Optional[str] = None,
        tool_calls: Optional[list] = None,
        tool_results: Optional[list] = None,
        execution_time_ms: Optional[int] = None,
        model_name: Optional[str] = None,
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, bool]:
        """Log AI interaction to all enabled logging systems.
        
        Returns:
            Dict with logging results: {"local": bool, "cloudwatch": bool}
        """
        results = {}
        
        # Log to local file
        results["local"] = self.local.log_ai_interaction(
            user_prompt=user_prompt,
            ai_response=ai_response,
            thinking=thinking,
            tool_calls=tool_calls,
            tool_results=tool_results,
            execution_time_ms=execution_time_ms,
            model_name=model_name,
            error=error,
            metadata=metadata
        )
        
        # Log to CloudWatch
        results["cloudwatch"] = self.cloudwatch.log_ai_interaction(
            user_prompt=user_prompt,
            ai_response=ai_response,
            thinking=thinking,
            tool_calls=tool_calls,
            tool_results=tool_results,
            execution_time_ms=execution_time_ms,
            model_name=model_name,
            error=error,
            metadata=metadata
        )
        
        return results
    
    def log_tool_execution(
        self,
        tool_name: str,
        tool_input: Dict[str, Any],
        tool_output: Any,
        execution_time_ms: int,
        success: bool,
        error: Optional[str] = None
    ) -> Dict[str, bool]:
        """Log tool execution to all enabled logging systems.
        
        Returns:
            Dict with logging results: {"local": bool, "cloudwatch": bool}
        """
        results = {}
        
        # Log to local file
        results["local"] = self.local.log_tool_execution(
            tool_name=tool_name,
            tool_input=tool_input,
            tool_output=tool_output,
            execution_time_ms=execution_time_ms,
            success=success,
            error=error
        )
        
        # Log to CloudWatch
        results["cloudwatch"] = self.cloudwatch.log_tool_execution(
            tool_name=tool_name,
            tool_input=tool_input,
            tool_output=tool_output,
            execution_time_ms=execution_time_ms,
            success=success,
            error=error
        )
        
        return results
    
    def log_system_event(
        self,
        event_type: str,
        message: str,
        level: str = "INFO",
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, bool]:
        """Log system event to all enabled logging systems.
        
        Returns:
            Dict with logging results: {"local": bool, "cloudwatch": bool}
        """
        results = {}
        
        # Log to local file
        results["local"] = self.local.log_system_event(
            event_type=event_type,
            message=message,
            level=level,
            data=data
        )
        
        # Log to CloudWatch
        results["cloudwatch"] = self.cloudwatch.log_system_event(
            event_type=event_type,
            message=message,
            level=level,
            data=data
        )
        
        return results
    
    @property
    def status(self) -> Dict[str, bool]:
        """Get the status of all logging systems."""
        return {
            "local": self.local.enabled,
            "cloudwatch": self.cloudwatch.enabled
        }


# Global AI logger instance
ai_logger = AILogger()