"""Snowflake Cortex Agent tools via MCP.

This module provides ONLY the tool that actually exists in the cortex-agent MCP server.
Based on Snowflake-Labs/sfguide-mcp-cortex-agents implementation.
"""

from meccaai.core.mcp_tool_base import mcp_tool

# ONLY actual cortex-agent MCP server tool (verified from Snowflake-Labs/sfguide-mcp-cortex-agents)


@mcp_tool(name="run_cortex_agents", server_name="cortex-agent")
def run_cortex_agents(query: str):
    """Run Cortex Agents to interact with Snowflake data and AI capabilities.

    Args:
        query: Query or request to process with Cortex Agents

    Returns:
        Results from Cortex Agents via MCP
    """
    pass  # Implementation handled by MCP decorator
