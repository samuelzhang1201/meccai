"""Base tool implementation and registry."""

import inspect
from collections.abc import Callable
from typing import Any

from meccaai.core.types import ToolResult


class BaseTool:
    """Base implementation of the Tool protocol."""

    def __init__(
        self,
        name: str,
        description: str,
        func: Callable,
        parameters_schema: dict[str, Any] | None = None,
    ):
        self._name = name
        self._description = description
        self._func = func
        self._parameters_schema = parameters_schema or self._generate_schema()

    @property
    def name(self) -> str:
        """Tool name identifier."""
        return self._name

    @property
    def description(self) -> str:
        """Tool description for AI agents."""
        return self._description

    @property
    def parameters(self) -> dict[str, Any]:
        """Tool parameters schema (JSON Schema format)."""
        return self._parameters_schema

    async def call(self, **kwargs: Any) -> ToolResult:
        """Execute the tool with given parameters."""
        try:
            if inspect.iscoroutinefunction(self._func):
                result = await self._func(**kwargs)
            else:
                result = self._func(**kwargs)

            return ToolResult(
                success=True,
                result=result,
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=str(e),
            )

    def _generate_schema(self) -> dict[str, Any]:
        """Generate JSON Schema from function signature."""
        sig = inspect.signature(self._func)
        properties = {}
        required = []

        for param_name, param in sig.parameters.items():
            if param_name == "self":
                continue

            param_schema = {"type": "string"}  # Default to string

            # Try to infer type from annotation
            if param.annotation != inspect.Parameter.empty:
                if param.annotation == int:
                    param_schema["type"] = "integer"
                elif param.annotation == float:
                    param_schema["type"] = "number"
                elif param.annotation == bool:
                    param_schema["type"] = "boolean"
                elif param.annotation == list:
                    param_schema["type"] = "array"
                elif param.annotation == dict:
                    param_schema["type"] = "object"

            # Add description from docstring if available
            if self._func.__doc__:
                # Simple extraction - could be enhanced with proper docstring parsing
                param_schema["description"] = f"Parameter {param_name}"

            properties[param_name] = param_schema

            # Required if no default value
            if param.default == inspect.Parameter.empty:
                required.append(param_name)

        return {
            "type": "object",
            "properties": properties,
            "required": required,
        }


def tool(name: str | None = None, description: str | None = None):
    """Decorator to create a tool from a function."""

    def decorator(func: Callable) -> BaseTool:
        tool_name = name or func.__name__
        tool_description = description or func.__doc__ or f"Tool: {tool_name}"

        tool_instance = BaseTool(
            name=tool_name,
            description=tool_description,
            func=func,
        )
        
        # Auto-register the tool
        from meccaai.core.tool_registry import get_registry
        get_registry().register(tool_instance)
        
        return tool_instance

    return decorator
