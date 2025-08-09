"""Example hello world tool."""

from meccaai.core.tool_base import tool


@tool(name="hello", description="Simple greeting tool")
def hello_tool(name: str = "World") -> str:
    """Generate a greeting message.

    Args:
        name: Name to greet (default: "World")

    Returns:
        Greeting message
    """
    return f"Hello, {name}!"


@tool(name="calculate", description="Perform basic calculations")
def calculate_tool(expression: str) -> str:
    """Safely evaluate a mathematical expression.

    Args:
        expression: Mathematical expression to evaluate (e.g., "2 + 2")

    Returns:
        Result of the calculation
    """
    try:
        # Only allow safe mathematical operations
        allowed_chars = set("0123456789+-*/.() ")
        if not all(c in allowed_chars for c in expression):
            return "Error: Invalid characters in expression"

        result = eval(expression, {"__builtins__": {}})
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"
