"""Test tools functionality."""

import pytest

from meccaai.core.tool_base import tool
from meccaai.core.tool_registry import get_registry


def test_basic_tool():
    """Test basic tool functionality."""

    @tool(name="test_tool", description="A test tool")
    def test_func(name: str) -> str:
        return f"Hello, {name}!"

    assert test_func.name == "test_tool"
    assert test_func.description == "A test tool"
    assert "name" in test_func.parameters["properties"]


@pytest.mark.asyncio
async def test_tool_execution():
    """Test tool execution."""

    @tool(name="calc", description="Simple calculator")
    def calc(a: int, b: int) -> int:
        return a + b

    result = await calc.call(a=2, b=3)
    assert result.success is True
    assert result.result == 5


@pytest.mark.asyncio
async def test_tool_error_handling():
    """Test tool error handling."""

    @tool(name="error_tool", description="Tool that raises error")
    def error_func():
        raise ValueError("Test error")

    result = await error_func.call()
    assert result.success is False
    assert "Test error" in str(result.error)


def test_tool_registry():
    """Test tool registry functionality."""
    registry = get_registry()
    registry.clear()

    @tool(name="registry_test", description="Registry test tool")
    def registry_test_func():
        return "test"

    registry.register(registry_test_func)

    assert registry.get_tool("registry_test") is not None
    assert len(registry.list_tools()) == 1

    registry.unregister("registry_test")
    assert registry.get_tool("registry_test") is None
    assert len(registry.list_tools()) == 0
