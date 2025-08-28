"""Local file logging system for AI interactions."""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional
import logging.handlers

from meccaai.core.config import settings


class LocalLogger:
    """Local file logger for AI prompts, responses, thinking, and datetime info."""
    
    def __init__(self):
        """Initialize local logger with configuration from settings."""
        self.config = getattr(settings, 'logging', {}).get('local', {})
        self.enabled = self.config.get('enabled', False)
        
        if not self.enabled:
            return
        
        # Setup file logging
        self.log_file = self.config.get('log_file', 'logs/ai_interactions.log')
        self.max_file_size = self.config.get('max_file_size_mb', 50) * 1024 * 1024  # Convert to bytes
        self.backup_count = self.config.get('backup_count', 10)
        self.log_level = self.config.get('log_level', 'DEBUG')
        
        # Ensure logs directory exists
        log_path = Path(self.log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Setup rotating file handler
        self.logger = logging.getLogger('meccaai.local')
        self.logger.setLevel(getattr(logging, self.log_level))
        
        # Remove existing handlers
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # Add rotating file handler
        handler = logging.handlers.RotatingFileHandler(
            self.log_file,
            maxBytes=self.max_file_size,
            backupCount=self.backup_count,
            encoding='utf-8'
        )
        
        # JSON formatter for structured logging
        formatter = logging.Formatter('%(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.propagate = False
    
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
    ) -> bool:
        """Log complete AI interaction with all details.
        
        Args:
            user_prompt: The user's input prompt
            ai_response: The AI's response
            thinking: Internal AI thinking/reasoning (if available)
            tool_calls: List of tools called during interaction
            tool_results: Results from tool executions
            execution_time_ms: Total execution time in milliseconds
            model_name: Name of the AI model used
            error: Error message if any occurred
            metadata: Additional metadata
            
        Returns:
            bool: True if logged successfully
        """
        if not self.enabled:
            return False
            
        try:
            log_entry = {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "event_type": "ai_interaction",
                "user_prompt": user_prompt,
                "ai_response": ai_response,
                "thinking": thinking,
                "tool_calls": tool_calls or [],
                "tool_results": tool_results or [],
                "execution_time_ms": execution_time_ms,
                "model_name": model_name,
                "error": error,
                "metadata": metadata or {},
                "session_id": getattr(settings, 'session_id', 'unknown')
            }
            
            # Convert to JSON and log
            json_log = json.dumps(log_entry, ensure_ascii=False, separators=(',', ':'))
            self.logger.info(json_log)
            return True
            
        except Exception as e:
            # Fallback logging to avoid breaking the application
            try:
                error_entry = {
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "event_type": "logging_error",
                    "error": str(e),
                    "message": "Failed to log AI interaction"
                }
                json_error = json.dumps(error_entry, ensure_ascii=False, separators=(',', ':'))
                self.logger.error(json_error)
            except:
                pass  # Silent failure to avoid infinite loops
            return False
    
    def log_tool_execution(
        self,
        tool_name: str,
        tool_input: Dict[str, Any],
        tool_output: Any,
        execution_time_ms: int,
        success: bool,
        error: Optional[str] = None
    ) -> bool:
        """Log individual tool execution details.
        
        Args:
            tool_name: Name of the executed tool
            tool_input: Input parameters
            tool_output: Tool output/result
            execution_time_ms: Execution time
            success: Whether execution was successful
            error: Error message if failed
            
        Returns:
            bool: True if logged successfully
        """
        if not self.enabled:
            return False
            
        try:
            log_entry = {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "event_type": "tool_execution",
                "tool_name": tool_name,
                "tool_input": tool_input,
                "tool_output": str(tool_output)[:10000] if tool_output else None,  # Limit size
                "execution_time_ms": execution_time_ms,
                "success": success,
                "error": error,
                "session_id": getattr(settings, 'session_id', 'unknown')
            }
            
            json_log = json.dumps(log_entry, ensure_ascii=False, separators=(',', ':'))
            self.logger.info(json_log)
            return True
            
        except Exception:
            return False
    
    def log_system_event(
        self,
        event_type: str,
        message: str,
        level: str = "INFO",
        data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Log system events and messages.
        
        Args:
            event_type: Type of system event
            message: Log message
            level: Log level (DEBUG, INFO, WARNING, ERROR)
            data: Additional data to log
            
        Returns:
            bool: True if logged successfully
        """
        if not self.enabled:
            return False
            
        try:
            log_entry = {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "event_type": event_type,
                "level": level.upper(),
                "message": message,
                "data": data or {},
                "session_id": getattr(settings, 'session_id', 'unknown')
            }
            
            json_log = json.dumps(log_entry, ensure_ascii=False, separators=(',', ':'))
            
            # Log at appropriate level
            log_method = getattr(self.logger, level.lower(), self.logger.info)
            log_method(json_log)
            return True
            
        except Exception:
            return False


# Global local logger instance
local_logger = LocalLogger()