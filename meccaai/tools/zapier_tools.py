"""Zapier integration tools via MCP.

This module provides access to Zapier's MCP server which dynamically exposes
tools based on user's configured Zapier automations. The actual tools available
depend on what apps and actions the user has set up in their Zapier account.

Note: Zapier MCP is a URL-based server that provides access to 7,000+ apps
and 30,000+ actions. Tools are dynamically generated based on user configuration.
"""

from meccaai.core.mcp_tool_base import mcp_tool

# Zapier MCP server provides dynamic tools based on user configuration
# The actual tools available depend on what the user has configured in their Zapier account
# Since tools are dynamic, we cannot pre-define them here

# Example tools that might be available (depending on user's Zapier setup):
# - Gmail: Send Email, Create Draft, etc.
# - Slack: Send Channel Message, Send Direct Message, etc. 
# - Google Sheets: Create Row, Update Row, etc.
# - Webhooks: POST Request, etc.
# - And thousands more based on connected apps

# To use Zapier MCP tools:
# 1. Configure your Zapier MCP server with the apps you want to use
# 2. The tools will be automatically available through the MCP protocol
# 3. Tools are accessed via the URL: https://mcp.zapier.com/api/mcp/s/[your-server-id]/mcp

# Since Zapier tools are dynamic and user-specific, no static tools are defined here.
# The MCP client will discover available tools at runtime from the Zapier server.