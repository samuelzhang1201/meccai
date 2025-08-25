"""AWS CloudWatch logging integration for AI responses and interactions."""

import json
import boto3
import time
from datetime import datetime
from typing import Any, Dict, Optional
from botocore.exceptions import ClientError, NoCredentialsError

from meccaai.core.config import settings
from meccaai.core.logging import get_logger

logger = get_logger(__name__)


class CloudWatchLogger:
    """AWS CloudWatch logger for AI responses and system events."""
    
    def __init__(self):
        """Initialize CloudWatch logs client and configuration."""
        self.log_group_name = getattr(settings, 'cloudwatch_log_group', '/meccaai/ai-responses')
        self.log_stream_name = f"ai-responses-{datetime.now().strftime('%Y-%m-%d')}"
        self.region_name = getattr(settings, 'aws_region', 'us-east-1')
        
        # Configurable truncation limits - ensure they are integers
        self.max_user_query_length = int(getattr(settings, 'cloudwatch_max_user_query_length', 5000))
        self.max_ai_response_length = int(getattr(settings, 'cloudwatch_max_ai_response_length', 10000))
        self.max_tool_output_length = int(getattr(settings, 'cloudwatch_max_tool_output_length', 50000))
        self.max_tool_input_length = int(getattr(settings, 'cloudwatch_max_tool_input_length', 10000))
        
        try:
            # Initialize CloudWatch Logs client
            self.cloudwatch_logs = boto3.client(
                'logs',
                region_name=self.region_name,
                aws_access_key_id=getattr(settings, 'aws_access_key_id', None),
                aws_secret_access_key=getattr(settings, 'aws_secret_access_key', None)
            )
            
            # Ensure log group and stream exist
            self._ensure_log_infrastructure()
            self.enabled = True
            
        except (NoCredentialsError, ClientError) as e:
            logger.warning(f"CloudWatch logging disabled: {e}")
            self.enabled = False
    
    def _ensure_log_infrastructure(self) -> None:
        """Ensure log group and stream exist in CloudWatch."""
        try:
            # Create log group if it doesn't exist
            try:
                self.cloudwatch_logs.create_log_group(logGroupName=self.log_group_name)
                logger.info(f"Created CloudWatch log group: {self.log_group_name}")
            except ClientError as e:
                if e.response['Error']['Code'] != 'ResourceAlreadyExistsException':
                    raise
            
            # Create log stream if it doesn't exist
            try:
                self.cloudwatch_logs.create_log_stream(
                    logGroupName=self.log_group_name,
                    logStreamName=self.log_stream_name
                )
                logger.info(f"Created CloudWatch log stream: {self.log_stream_name}")
            except ClientError as e:
                if e.response['Error']['Code'] != 'ResourceAlreadyExistsException':
                    raise
                    
        except ClientError as e:
            logger.error(f"Failed to ensure CloudWatch log infrastructure: {e}")
            raise
    
    def _truncate_string(self, text: str, max_length: int, field_name: str = "text") -> str:
        """Truncate string with warning if needed."""
        try:
            # Ensure max_length is an integer
            max_length = int(max_length)
            
            # Handle None or empty text
            if not text:
                return text
            
            # Convert to string if needed
            text_str = str(text)
            
            if len(text_str) > max_length:
                truncated_text = text_str[:max_length]
                logger.warning(f"CloudWatch log {field_name} truncated from {len(text_str)} to {max_length} characters")
                return truncated_text + f"\n... [TRUNCATED - Original length: {len(text_str)} characters]"
            return text_str
            
        except (ValueError, TypeError) as e:
            logger.error(f"Error in _truncate_string for {field_name}: {e}")
            # Return original text if truncation fails
            return str(text) if text else ""
    
    def log_ai_response(
        self, 
        user_query: str,
        ai_response: str,
        tool_calls: Optional[list] = None,
        execution_time_ms: Optional[int] = None,
        model_name: Optional[str] = None,
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Log AI response to CloudWatch.
        
        Args:
            user_query: The user's input query
            ai_response: The AI's response
            tool_calls: List of tools called during response generation
            execution_time_ms: Time taken to generate response in milliseconds
            model_name: Name of the AI model used
            error: Error message if any occurred
            metadata: Additional metadata to log
        
        Returns:
            bool: True if logged successfully, False otherwise
        """
        if not self.enabled:
            return False
        
        try:
            # Prepare log entry with configurable truncation
            log_entry = {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "user_query": self._truncate_string(user_query, self.max_user_query_length, "user_query"),
                "ai_response": self._truncate_string(ai_response, self.max_ai_response_length, "ai_response") if ai_response else None,
                "tool_calls": tool_calls,
                "execution_time_ms": execution_time_ms,
                "model_name": model_name,
                "error": error,
                "metadata": metadata or {},
                "session_id": getattr(settings, 'session_id', 'unknown')
            }
            
            # Send to CloudWatch
            self._send_log_event(log_entry, "AI_RESPONSE")
            return True
            
        except Exception as e:
            logger.error(f"Failed to log AI response to CloudWatch: {e}")
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
        """Log tool execution details to CloudWatch.
        
        Args:
            tool_name: Name of the executed tool
            tool_input: Input parameters passed to the tool
            tool_output: Output returned by the tool
            execution_time_ms: Execution time in milliseconds
            success: Whether tool execution was successful
            error: Error message if execution failed
        
        Returns:
            bool: True if logged successfully, False otherwise
        """
        if not self.enabled:
            return False
        
        try:
            # Convert tool output to string and truncate if needed
            tool_output_str = str(tool_output) if tool_output else None
            truncated_tool_output = self._truncate_string(tool_output_str, self.max_tool_output_length, "tool_output") if tool_output_str else None
            
            # Truncate tool input if it's too large
            try:
                tool_input_str = json.dumps(tool_input, default=str, ensure_ascii=False)
            except (TypeError, ValueError) as e:
                logger.warning(f"Failed to serialize tool input: {e}")
                tool_input_str = str(tool_input)
            
            truncated_tool_input = self._truncate_string(tool_input_str, self.max_tool_input_length, "tool_input")
            
            log_entry = {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "tool_name": tool_name,
                "tool_input": truncated_tool_input,
                "tool_output": truncated_tool_output,
                "execution_time_ms": execution_time_ms,
                "success": success,
                "error": error,
                "session_id": getattr(settings, 'session_id', 'unknown')
            }
            
            self._send_log_event(log_entry, "TOOL_EXECUTION")
            return True
            
        except Exception as e:
            logger.error(f"Failed to log tool execution to CloudWatch: {e}")
            return False
    
    def log_system_event(
        self,
        event_type: str,
        event_data: Dict[str, Any],
        level: str = "INFO"
    ) -> bool:
        """Log system events to CloudWatch.
        
        Args:
            event_type: Type of system event
            event_data: Event data to log
            level: Log level (INFO, WARN, ERROR)
        
        Returns:
            bool: True if logged successfully, False otherwise
        """
        if not self.enabled:
            return False
        
        try:
            log_entry = {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "event_type": event_type,
                "level": level,
                "event_data": event_data,
                "session_id": getattr(settings, 'session_id', 'unknown')
            }
            
            self._send_log_event(log_entry, "SYSTEM_EVENT")
            return True
            
        except Exception as e:
            logger.error(f"Failed to log system event to CloudWatch: {e}")
            return False
    
    def _send_log_event(self, log_entry: Dict[str, Any], log_type: str) -> None:
        """Send log event to CloudWatch Logs.
        
        Args:
            log_entry: Log data to send
            log_type: Type of log entry
        """
        try:
            # Add log type to entry
            log_entry["log_type"] = log_type
            
            # Convert to JSON string
            message = json.dumps(log_entry, default=str, ensure_ascii=False)
            
            # Get sequence token for the log stream
            sequence_token = self._get_sequence_token()
            
            # Prepare log event
            log_event = {
                'timestamp': int(time.time() * 1000),
                'message': message
            }
            
            # Send to CloudWatch
            put_log_events_kwargs = {
                'logGroupName': self.log_group_name,
                'logStreamName': self.log_stream_name,
                'logEvents': [log_event]
            }
            
            if sequence_token:
                put_log_events_kwargs['sequenceToken'] = sequence_token
            
            response = self.cloudwatch_logs.put_log_events(**put_log_events_kwargs)
            
            # Update sequence token for next use
            self._last_sequence_token = response.get('nextSequenceToken')
            
        except ClientError as e:
            logger.error(f"Failed to send log event to CloudWatch: {e}")
            raise
    
    def _get_sequence_token(self) -> Optional[str]:
        """Get the latest sequence token for the log stream."""
        try:
            # Use cached token if available
            if hasattr(self, '_last_sequence_token'):
                return self._last_sequence_token
            
            # Get token from CloudWatch
            response = self.cloudwatch_logs.describe_log_streams(
                logGroupName=self.log_group_name,
                logStreamNamePrefix=self.log_stream_name,
                limit=1
            )
            
            streams = response.get('logStreams', [])
            if streams:
                return streams[0].get('uploadSequenceToken')
            
            return None
            
        except ClientError:
            return None


# Global CloudWatch logger instance
cloudwatch_logger = CloudWatchLogger()