"""CloudWatch logging system for AI interactions."""

import json
import time
from datetime import datetime
from typing import Any, Dict, Optional

try:
    import boto3
    from botocore.exceptions import ClientError, NoCredentialsError
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False

from meccaai.core.config import settings


class CloudWatchLogger:
    """CloudWatch logger for AI interactions."""
    
    def __init__(self):
        """Initialize CloudWatch logger with configuration from settings."""
        self.config = getattr(settings, 'logging', {}).get('cloudwatch', {})
        self.enabled = self.config.get('enabled', False)
        
        if not self.enabled:
            return
        
        if not BOTO3_AVAILABLE:
            print("Warning: boto3 not available. CloudWatch logging disabled.")
            self.enabled = False
            return
        
        # Configuration
        self.log_group = self.config.get('log_group', '/meccaai/ai-interactions')
        self.log_stream_prefix = self.config.get('log_stream_prefix', 'ai-session')
        self.log_level = self.config.get('log_level', 'INFO')
        self.max_message_size = self.config.get('max_message_size', 256000)
        
        # Generate unique log stream name with timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        self.log_stream_name = f"{self.log_stream_prefix}-{timestamp}"
        
        # AWS region from bedrock config
        self.region_name = getattr(settings, 'bedrock', {}).get('aws_region', 'us-east-1')
        
        try:
            # Initialize CloudWatch Logs client
            self.client = boto3.client(
                'logs',
                region_name=self.region_name,
                aws_access_key_id=getattr(settings, 'bedrock', {}).get('aws_access_key_id', None),
                aws_secret_access_key=getattr(settings, 'bedrock', {}).get('aws_secret_access_key', None)
            )
            
            # Ensure log group and stream exist
            self._ensure_log_infrastructure()
            
        except (NoCredentialsError, ClientError) as e:
            print(f"Warning: CloudWatch logging disabled due to AWS error: {e}")
            self.enabled = False
    
    def _ensure_log_infrastructure(self) -> None:
        """Ensure log group and stream exist."""
        try:
            # Create log group if it doesn't exist
            try:
                self.client.create_log_group(logGroupName=self.log_group)
            except ClientError as e:
                if e.response['Error']['Code'] != 'ResourceAlreadyExistsException':
                    raise
            
            # Create log stream if it doesn't exist
            try:
                self.client.create_log_stream(
                    logGroupName=self.log_group,
                    logStreamName=self.log_stream_name
                )
            except ClientError as e:
                if e.response['Error']['Code'] != 'ResourceAlreadyExistsException':
                    raise
                    
        except ClientError as e:
            raise Exception(f"Failed to setup CloudWatch infrastructure: {e}")
    
    def _truncate_message(self, message: str) -> str:
        """Truncate message if it exceeds CloudWatch limits."""
        if len(message) <= self.max_message_size:
            return message
        
        # Truncate and add notice
        truncated = message[:self.max_message_size - 100]
        return truncated + f"\n... [TRUNCATED - Original size: {len(message)} chars]"
    
    def _send_log_event(self, log_entry: Dict[str, Any]) -> bool:
        """Send log event to CloudWatch."""
        if not self.enabled:
            return False
        
        try:
            # Convert to JSON and truncate if needed
            message = json.dumps(log_entry, ensure_ascii=False, separators=(',', ':'))
            message = self._truncate_message(message)
            
            # Get sequence token
            sequence_token = self._get_sequence_token()
            
            # Prepare log event
            log_event = {
                'timestamp': int(time.time() * 1000),
                'message': message
            }
            
            # Send to CloudWatch
            kwargs = {
                'logGroupName': self.log_group,
                'logStreamName': self.log_stream_name,
                'logEvents': [log_event]
            }
            
            if sequence_token:
                kwargs['sequenceToken'] = sequence_token
            
            response = self.client.put_log_events(**kwargs)
            
            # Update sequence token for next use
            self._sequence_token = response.get('nextSequenceToken')
            return True
            
        except Exception as e:
            print(f"CloudWatch logging error: {e}")
            return False
    
    def _get_sequence_token(self) -> Optional[str]:
        """Get the latest sequence token for the log stream."""
        try:
            # Use cached token if available
            if hasattr(self, '_sequence_token'):
                return self._sequence_token
            
            # Get token from CloudWatch
            response = self.client.describe_log_streams(
                logGroupName=self.log_group,
                logStreamNamePrefix=self.log_stream_name,
                limit=1
            )
            
            streams = response.get('logStreams', [])
            if streams:
                return streams[0].get('uploadSequenceToken')
                
        except Exception:
            pass
        
        return None
    
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
        """Log AI interaction to CloudWatch."""
        if not self.enabled:
            return False
        
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "event_type": "ai_interaction",
            "user_prompt": user_prompt[:5000] if user_prompt else None,  # Truncate for CloudWatch
            "ai_response": ai_response[:10000] if ai_response else None,
            "thinking": thinking[:5000] if thinking else None,
            "tool_calls": tool_calls or [],
            "tool_results": [str(result)[:2000] for result in (tool_results or [])],  # Truncate results
            "execution_time_ms": execution_time_ms,
            "model_name": model_name,
            "error": error,
            "metadata": metadata or {},
            "session_id": getattr(settings, 'session_id', 'unknown')
        }
        
        return self._send_log_event(log_entry)
    
    def log_tool_execution(
        self,
        tool_name: str,
        tool_input: Dict[str, Any],
        tool_output: Any,
        execution_time_ms: int,
        success: bool,
        error: Optional[str] = None
    ) -> bool:
        """Log tool execution to CloudWatch."""
        if not self.enabled:
            return False
        
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "event_type": "tool_execution",
            "tool_name": tool_name,
            "tool_input": str(tool_input)[:2000],  # Truncate for CloudWatch
            "tool_output": str(tool_output)[:5000] if tool_output else None,
            "execution_time_ms": execution_time_ms,
            "success": success,
            "error": error,
            "session_id": getattr(settings, 'session_id', 'unknown')
        }
        
        return self._send_log_event(log_entry)
    
    def log_system_event(
        self,
        event_type: str,
        message: str,
        level: str = "INFO",
        data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Log system event to CloudWatch."""
        if not self.enabled:
            return False
        
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "event_type": event_type,
            "level": level.upper(),
            "message": message,
            "data": data or {},
            "session_id": getattr(settings, 'session_id', 'unknown')
        }
        
        return self._send_log_event(log_entry)


# Global CloudWatch logger instance
cloudwatch_logger = CloudWatchLogger()