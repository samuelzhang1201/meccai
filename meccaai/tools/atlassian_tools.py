"""Atlassian integration tools via MCP.

This module provides ONLY the tools that actually exist in Jira MCP servers.
Based on cosmix/jira-mcp server implementation.
"""

from meccaai.core.mcp_tool_base import mcp_tool

# ONLY actual Jira MCP server tools (verified from cosmix/jira-mcp)
# Note: Using Jira MCP server, not a combined Atlassian server


@mcp_tool(name="search_issues", server_name="jira-mcp")
def search_issues(jql: str, max_results: int = 50):
    """Search JIRA issues using JQL. Returns up to 50 results per request.

    Args:
        jql: JQL query string
        max_results: Maximum number of results to return (default: 50)

    Returns:
        Search results from Jira via MCP
    """
    pass  # Implementation handled by MCP decorator


@mcp_tool(name="get_epic_children", server_name="jira-mcp")
def get_epic_children(epic_key: str):
    """Get children of an epic.

    Args:
        epic_key: The epic key to get children for

    Returns:
        List of epic children via MCP
    """
    pass  # Implementation handled by MCP decorator


@mcp_tool(name="get_issue", server_name="jira-mcp")
def get_issue(issue_key: str):
    """Get details of a specific Jira issue.

    Args:
        issue_key: The Jira issue key

    Returns:
        Issue details via MCP
    """
    pass  # Implementation handled by MCP decorator


@mcp_tool(name="create_issue", server_name="jira-mcp")
def create_issue(
    project_key: str,
    summary: str,
    issue_type: str,
    description: str | None = None,
    priority: str | None = None,
):
    """Create a new Jira issue.

    Args:
        project_key: The Jira project key
        summary: Brief summary of the issue
        issue_type: Type of issue (Bug, Task, Story, etc.)
        description: Detailed description of the issue
        priority: Priority level of the issue

    Returns:
        Issue creation result via MCP
    """
    pass  # Implementation handled by MCP decorator


@mcp_tool(name="update_issue", server_name="jira-mcp")
def update_issue(
    issue_key: str,
    summary: str | None = None,
    description: str | None = None,
    assignee: str | None = None,
    status: str | None = None,
):
    """Update an existing Jira issue.

    Args:
        issue_key: The Jira issue key to update
        summary: Updated summary
        description: Updated description
        assignee: Updated assignee
        status: Updated status

    Returns:
        Update result via MCP
    """
    pass  # Implementation handled by MCP decorator


@mcp_tool(name="add_attachment", server_name="jira-mcp")
def add_attachment(issue_key: str, file_path: str):
    """Add an attachment to a Jira issue.

    Args:
        issue_key: The Jira issue key
        file_path: Path to the file to attach

    Returns:
        Attachment result via MCP
    """
    pass  # Implementation handled by MCP decorator


@mcp_tool(name="add_comment", server_name="jira-mcp")
def add_comment(issue_key: str, comment: str):
    """Add a comment to a Jira issue.

    Args:
        issue_key: The Jira issue key
        comment: Comment text to add

    Returns:
        Comment addition result via MCP
    """
    pass  # Implementation handled by MCP decorator
