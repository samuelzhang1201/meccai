"""Base class for MCP-based tools."""

from typing import Any

from meccaai.core.logging import get_logger
from meccaai.core.mcp_client import MCPClient, load_mcp_servers_config
from meccaai.core.tool_base import BaseTool
from meccaai.core.types import ToolResult

logger = get_logger(__name__)


class MCPTool(BaseTool):
    """Base class for tools that call MCP servers."""

    def __init__(
        self,
        name: str,
        description: str,
        server_name: str,
        mcp_tool_name: str | None = None,
        parameters_schema: dict[str, Any] | None = None,
    ):
        # Don't pass func to parent since we override call method
        super().__init__(
            name=name,
            description=description,
            func=lambda: None,  # Dummy function
            parameters_schema=parameters_schema,
        )
        self.server_name = server_name
        self.mcp_tool_name = mcp_tool_name or name
        self._mcp_client: MCPClient | None = None

    async def _get_mcp_client(self) -> MCPClient:
        """Get or create MCP client."""
        if self._mcp_client is None:
            self._mcp_client = MCPClient()
            
            # Load and start servers
            servers = load_mcp_servers_config("config/mcp/cursor.mcp.json")
            for server in servers:
                if server.name == self.server_name:
                    await self._mcp_client.start_server(server)
                    break
            else:
                raise ValueError(f"MCP server '{self.server_name}' not found in config")
                
        return self._mcp_client

    async def call(self, **kwargs: Any) -> ToolResult:
        """Execute the tool via MCP server."""
        try:
            client = await self._get_mcp_client()
            
            # Call the MCP tool
            result = await client.call_tool(
                server_name=self.server_name,
                tool_name=self.mcp_tool_name,
                arguments=kwargs
            )
            
            return ToolResult(
                success=True,
                result=result,
            )
            
        except Exception as e:
            logger.error(f"MCP tool call failed for {self.name}: {e}")
            return ToolResult(
                success=False,
                error=str(e),
            )

    async def __del__(self):
        """Cleanup MCP client."""
        if self._mcp_client:
            await self._mcp_client.cleanup()


def mcp_tool(
    name: str | None = None,
    description: str | None = None, 
    server_name: str = "dbt-mcp",
    mcp_tool_name: str | None = None,
):
    """Decorator to create an MCP tool."""
    
    def decorator(func) -> MCPTool:
        import inspect
        
        tool_name = name or func.__name__
        tool_description = description or func.__doc__ or f"MCP Tool: {tool_name}"
        
        # Extract parameters schema from function signature if available
        sig = inspect.signature(func)
        parameters_schema = _generate_schema_from_signature(sig)
        
        tool_instance = MCPTool(
            name=tool_name,
            description=tool_description,
            server_name=server_name,
            mcp_tool_name=mcp_tool_name,
            parameters_schema=parameters_schema,
        )
        
        # Auto-register the tool
        from meccaai.core.tool_registry import get_registry
        get_registry().register(tool_instance)
        
        return tool_instance
    
    return decorator


def _generate_schema_from_signature(sig) -> dict[str, Any]:
    """Generate JSON Schema from function signature."""
    properties = {}
    required = []

    for param_name, param in sig.parameters.items():
        if param_name == "self":
            continue

        param_schema = {"type": "string"}  # Default to string

        # Try to infer type from annotation  
        import inspect
        if param.annotation != inspect.Parameter.empty:
            if param.annotation is int:
                param_schema["type"] = "integer"
            elif param.annotation is float:
                param_schema["type"] = "number"
            elif param.annotation is bool:
                param_schema["type"] = "boolean"
            elif param.annotation is list:
                param_schema["type"] = "array"
            elif param.annotation is dict:
                param_schema["type"] = "object"

        properties[param_name] = param_schema

        # Required if no default value
        if param.default == inspect.Parameter.empty:
            required.append(param_name)

    return {
        "type": "object",
        "properties": properties,
        "required": required,
    }