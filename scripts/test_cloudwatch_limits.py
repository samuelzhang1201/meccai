#!/usr/bin/env python3
"""Test script for CloudWatch logger limits."""

import asyncio
import time
from meccaai.core.cloudwatch_logger import cloudwatch_logger

def test_cloudwatch_limits():
    """Test CloudWatch logger with different data sizes."""
    print("🧪 Testing CloudWatch Logger Limits...")
    
    # Test 1: Small tool output (should not be truncated)
    print("\n📝 Test 1: Small tool output (500 chars)")
    small_output = "A" * 500
    success = cloudwatch_logger.log_tool_execution(
        tool_name="test_small_tool",
        tool_input={"param": "value"},
        tool_output=small_output,
        execution_time_ms=100,
        success=True
    )
    print(f"✅ Small output logged: {success}")
    
    # Test 2: Medium tool output (should not be truncated with new limits)
    print("\n📝 Test 2: Medium tool output (50,000 chars)")
    medium_output = "B" * 50000
    success = cloudwatch_logger.log_tool_execution(
        tool_name="test_medium_tool",
        tool_input={"param": "value", "data": "test"},
        tool_output=medium_output,
        execution_time_ms=200,
        success=True
    )
    print(f"✅ Medium output logged: {success}")
    
    # Test 3: Large tool output (should be truncated but with much higher limit)
    print("\n📝 Test 3: Large tool output (150,000 chars)")
    large_output = "C" * 150000
    success = cloudwatch_logger.log_tool_execution(
        tool_name="test_large_tool",
        tool_input={"param": "value", "data": "test", "config": "large"},
        tool_output=large_output,
        execution_time_ms=500,
        success=True
    )
    print(f"✅ Large output logged: {success}")
    
    # Test 4: Very large tool output (should be truncated with warning)
    print("\n📝 Test 4: Very large tool output (250,000 chars)")
    very_large_output = "D" * 250000
    success = cloudwatch_logger.log_tool_execution(
        tool_name="test_very_large_tool",
        tool_input={"param": "value", "data": "test", "config": "very_large"},
        tool_output=very_large_output,
        execution_time_ms=1000,
        success=True
    )
    print(f"✅ Very large output logged: {success}")
    
    # Test 5: AI response with new limits
    print("\n📝 Test 5: AI response (40,000 chars)")
    ai_response = "This is a detailed AI response with lots of information. " * 800  # ~40,000 chars
    success = cloudwatch_logger.log_ai_response(
        user_query="Test query for AI response",
        ai_response=ai_response,
        tool_calls=[{"name": "test_tool"}],
        execution_time_ms=3000,
        model_name="test-model"
    )
    print(f"✅ AI response logged: {success}")
    
    print("\n✅ CloudWatch logger limit tests completed!")
    print("📊 Check your CloudWatch console for the test logs")
    print("🔍 Look for truncation warnings in the application logs")

if __name__ == "__main__":
    test_cloudwatch_limits()
