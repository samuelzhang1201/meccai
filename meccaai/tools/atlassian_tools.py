"""Atlassian (Jira & Confluence) integration tools.

This module provides comprehensive Jira and Confluence tools based on 
atlassian-mcp-server functionality with enhanced filtering capabilities.
"""

from typing import Any, Dict, List, Optional

import httpx

from meccaai.core.config import settings
from meccaai.core.logging import get_logger
from meccaai.core.tool_base import tool
from meccaai.core.types import ToolResult

logger = get_logger(__name__)


class AtlassianAuthManager:
    """Manages Atlassian authentication supporting multiple auth methods."""

    def __init__(self):
        self.jira_base_url = getattr(settings, 'jira_base_url', None)
        self.confluence_base_url = getattr(settings, 'confluence_base_url', None)
        
        # Support multiple authentication methods
        self.auth_method = getattr(settings, 'atlassian_auth_method', 'sso')  # 'sso', 'token', 'oauth'
        
        # Token-based auth (fallback)
        self.api_token = getattr(settings, 'atlassian_api_token', None)
        self.email = getattr(settings, 'atlassian_email', None)
        
        # SSO/Session-based auth
        self.session_token = getattr(settings, 'atlassian_session_token', None)
        self.cookies = getattr(settings, 'atlassian_cookies', None)
        
        # OAuth 2.0 auth  
        self.oauth_token = getattr(settings, 'atlassian_oauth_token', None)

    def get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers based on configured auth method."""
        base_headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        if self.auth_method == 'sso' and self.session_token:
            # SSO session-based authentication
            base_headers["Authorization"] = f"Bearer {self.session_token}"
            return base_headers
            
        elif self.auth_method == 'oauth' and self.oauth_token:
            # OAuth 2.0 authentication
            base_headers["Authorization"] = f"Bearer {self.oauth_token}"
            return base_headers
            
        elif self.auth_method == 'token' and self.api_token and self.email:
            # Basic auth with API token (fallback)
            import base64
            auth_string = f"{self.email}:{self.api_token}"
            auth_bytes = base64.b64encode(auth_string.encode()).decode()
            base_headers["Authorization"] = f"Basic {auth_bytes}"
            return base_headers
        else:
            # No authentication configured - return basic headers for testing
            logger.warning("No Atlassian authentication configured. API calls may fail.")
            return base_headers
    
    def get_cookies(self) -> Optional[Dict[str, str]]:
        """Get session cookies if available for SSO authentication."""
        if self.auth_method == 'sso' and self.cookies:
            if isinstance(self.cookies, str):
                # Parse cookie string into dict
                cookies = {}
                for cookie in self.cookies.split(';'):
                    if '=' in cookie:
                        key, value = cookie.strip().split('=', 1)
                        cookies[key] = value
                return cookies
            return self.cookies
        return None
    
    async def make_request(self, client: httpx.AsyncClient, method: str, url: str, **kwargs) -> httpx.Response:
        """Make authenticated request with proper headers and cookies."""
        # Add authentication headers
        if "headers" not in kwargs:
            kwargs["headers"] = {}
        kwargs["headers"].update(self.get_auth_headers())
        
        # Add cookies for SSO authentication
        cookies = self.get_cookies()
        if cookies:
            kwargs["cookies"] = cookies
        
        # Set default timeout
        if "timeout" not in kwargs:
            kwargs["timeout"] = 30.0
            
        # Make the request
        return await client.request(method, url, **kwargs)


# ============================================================================
# JIRA TOOLS
# ============================================================================

@tool("get_jira_issue")
async def get_jira_issue(
    issue_key: str,
    fields: str = "summary,description,status,assignee,priority,created,updated",
    expand: str = ""
) -> ToolResult:
    """Get details of a specific Jira issue with field filtering.

    Args:
        issue_key: The Jira issue key (e.g., "PROJ-123")
        fields: Comma-separated list of fields to return (default: key fields)
        expand: Comma-separated list of fields to expand (e.g., "changelog,comments")

    Returns:
        ToolResult: Detailed issue information
    """
    auth_manager = AtlassianAuthManager()
    
    if not auth_manager.jira_base_url:
        return ToolResult(
            success=False,
            result={"error": "Jira base URL not configured"}
        )
    
    try:
        url = f"{auth_manager.jira_base_url}/rest/api/3/issue/{issue_key}"
        params = {}
        
        if fields:
            params["fields"] = fields
        if expand:
            params["expand"] = expand

        async with httpx.AsyncClient() as client:
            response = await auth_manager.make_request(
                client, "GET", url, params=params
            )
            response.raise_for_status()
            
            issue_data = response.json()
            
            return ToolResult(
                success=True,
                result={
                    "issue": issue_data,
                    "key": issue_data.get("key"),
                    "summary": issue_data.get("fields", {}).get("summary"),
                    "status": issue_data.get("fields", {}).get("status", {}).get("name")
                }
            )
            
    except Exception as e:
        logger.error(f"Error getting Jira issue {issue_key}: {e}")
        return ToolResult(
            success=False,
            result={"error": f"Failed to get issue: {str(e)}"}
        )


@tool("edit_jira_issue")
async def edit_jira_issue(
    issue_key: str,
    summary: Optional[str] = None,
    description: Optional[str] = None,
    assignee: Optional[str] = None,
    priority: Optional[str] = None,
    status: Optional[str] = None,
    labels: Optional[List[str]] = None
) -> ToolResult:
    """Edit/update an existing Jira issue.

    Args:
        issue_key: The Jira issue key to update
        summary: Updated summary/title
        description: Updated description
        assignee: Updated assignee (email or account ID)
        priority: Updated priority (e.g., "High", "Medium", "Low")
        status: Updated status (must be valid transition)
        labels: Updated labels list

    Returns:
        ToolResult: Update result
    """
    auth_manager = AtlassianAuthManager()
    
    if not auth_manager.jira_base_url:
        return ToolResult(
            success=False,
            result={"error": "Jira base URL not configured"}
        )
    
    try:
        url = f"{auth_manager.jira_base_url}/rest/api/3/issue/{issue_key}"
        
        # Build update payload
        update_fields = {}
        if summary is not None:
            update_fields["summary"] = summary
        if description is not None:
            update_fields["description"] = {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": description}]
                    }
                ]
            }
        if assignee is not None:
            update_fields["assignee"] = {"accountId": assignee} if assignee else None
        if priority is not None:
            update_fields["priority"] = {"name": priority}
        if labels is not None:
            update_fields["labels"] = [{"add": label} for label in labels]

        payload = {"fields": update_fields}

        async with httpx.AsyncClient() as client:
            response = await client.put(
                url,
                json=payload,
                headers=auth_manager.get_auth_headers(),
                timeout=30.0
            )
            response.raise_for_status()
            
            # Handle status transition separately if provided
            if status is not None:
                transition_url = f"{url}/transitions"
                # Get available transitions
                transitions_response = await client.get(
                    transition_url,
                    headers=auth_manager.get_auth_headers()
                )
                transitions_data = transitions_response.json()
                
                # Find matching transition
                target_transition = None
                for transition in transitions_data.get("transitions", []):
                    if transition["to"]["name"].lower() == status.lower():
                        target_transition = transition["id"]
                        break
                
                if target_transition:
                    await client.post(
                        transition_url,
                        json={"transition": {"id": target_transition}},
                        headers=auth_manager.get_auth_headers()
                    )
            
            return ToolResult(
                success=True,
                result={
                    "message": f"Successfully updated issue {issue_key}",
                    "issue_key": issue_key,
                    "updated_fields": list(update_fields.keys())
                }
            )
            
    except Exception as e:
        logger.error(f"Error updating Jira issue {issue_key}: {e}")
        return ToolResult(
            success=False,
            result={"error": f"Failed to update issue: {str(e)}"}
        )


@tool("create_jira_issue")
async def create_jira_issue(
    project_key: str,
    issue_type: str,
    summary: str,
    description: Optional[str] = None,
    priority: str = "Medium",
    assignee: Optional[str] = None,
    labels: Optional[List[str]] = None
) -> ToolResult:
    """Create a new Jira issue.

    Args:
        project_key: The Jira project key (e.g., "PROJ")
        issue_type: Issue type (e.g., "Bug", "Task", "Story")
        summary: Brief summary/title of the issue
        description: Detailed description of the issue
        priority: Priority level ("High", "Medium", "Low")
        assignee: Assignee email or account ID
        labels: List of labels to add

    Returns:
        ToolResult: Created issue details
    """
    auth_manager = AtlassianAuthManager()
    
    if not auth_manager.jira_base_url:
        return ToolResult(
            success=False,
            result={"error": "Jira base URL not configured"}
        )
    
    try:
        url = f"{auth_manager.jira_base_url}/rest/api/3/issue"
        
        # Build issue payload
        fields = {
            "project": {"key": project_key},
            "issuetype": {"name": issue_type},
            "summary": summary,
            "priority": {"name": priority}
        }
        
        if description:
            fields["description"] = {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": description}]
                    }
                ]
            }
        
        if assignee:
            fields["assignee"] = {"accountId": assignee}
        
        if labels:
            fields["labels"] = [{"name": label} for label in labels]

        payload = {"fields": fields}

        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json=payload,
                headers=auth_manager.get_auth_headers(),
                timeout=30.0
            )
            response.raise_for_status()
            
            result_data = response.json()
            
            return ToolResult(
                success=True,
                result={
                    "issue_key": result_data.get("key"),
                    "issue_id": result_data.get("id"),
                    "url": f"{auth_manager.jira_base_url}/browse/{result_data.get('key')}",
                    "message": f"Successfully created issue {result_data.get('key')}"
                }
            )
            
    except Exception as e:
        logger.error(f"Error creating Jira issue: {e}")
        return ToolResult(
            success=False,
            result={"error": f"Failed to create issue: {str(e)}"}
        )


@tool("search_jira_issues_using_jql")
async def search_jira_issues_using_jql(
    jql: str,
    max_results: int = 50,
    start_at: int = 0,
    fields: str = "key,summary,status,assignee,priority,created,updated",
    expand: str = ""
) -> ToolResult:
    """Search Jira issues using JQL with filtering and pagination.

    Args:
        jql: JQL query string (e.g., "project = PROJ AND status = Open")
        max_results: Maximum number of results (1-1000, default 50)
        start_at: Starting index for pagination (default 0)
        fields: Comma-separated fields to return
        expand: Comma-separated fields to expand (e.g., "changelog,comments")

    Returns:
        ToolResult: Search results with issues
    """
    auth_manager = AtlassianAuthManager()
    
    if not auth_manager.jira_base_url:
        return ToolResult(
            success=False,
            result={"error": "Jira base URL not configured"}
        )
    
    try:
        url = f"{auth_manager.jira_base_url}/rest/api/3/search"
        
        params = {
            "jql": jql,
            "maxResults": min(max(max_results, 1), 1000),
            "startAt": max(start_at, 0)
        }
        
        if fields:
            params["fields"] = fields
        if expand:
            params["expand"] = expand

        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                params=params,
                headers=auth_manager.get_auth_headers(),
                timeout=30.0
            )
            response.raise_for_status()
            
            search_data = response.json()
            
            return ToolResult(
                success=True,
                result={
                    "total": search_data.get("total", 0),
                    "issues": search_data.get("issues", []),
                    "start_at": search_data.get("startAt", 0),
                    "max_results": search_data.get("maxResults", 0),
                    "jql_query": jql
                }
            )
            
    except Exception as e:
        logger.error(f"Error searching Jira issues: {e}")
        return ToolResult(
            success=False,
            result={"error": f"Failed to search issues: {str(e)}"}
        )


@tool("add_comment_to_jira_issue")
async def add_comment_to_jira_issue(
    issue_key: str,
    comment: str,
    visibility: Optional[str] = None
) -> ToolResult:
    """Add a comment to a Jira issue.

    Args:
        issue_key: The Jira issue key (e.g., "PROJ-123")
        comment: Comment text to add
        visibility: Comment visibility restriction (optional)

    Returns:
        ToolResult: Comment creation result
    """
    auth_manager = AtlassianAuthManager()
    
    if not auth_manager.jira_base_url:
        return ToolResult(
            success=False,
            result={"error": "Jira base URL not configured"}
        )
    
    try:
        url = f"{auth_manager.jira_base_url}/rest/api/3/issue/{issue_key}/comment"
        
        # Build comment payload
        payload = {
            "body": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": comment}]
                    }
                ]
            }
        }
        
        if visibility:
            payload["visibility"] = {"type": "role", "value": visibility}

        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json=payload,
                headers=auth_manager.get_auth_headers(),
                timeout=30.0
            )
            response.raise_for_status()
            
            result_data = response.json()
            
            return ToolResult(
                success=True,
                result={
                    "comment_id": result_data.get("id"),
                    "issue_key": issue_key,
                    "author": result_data.get("author", {}).get("displayName"),
                    "created": result_data.get("created"),
                    "message": f"Successfully added comment to {issue_key}"
                }
            )
            
    except Exception as e:
        logger.error(f"Error adding comment to Jira issue {issue_key}: {e}")
        return ToolResult(
            success=False,
            result={"error": f"Failed to add comment: {str(e)}"}
        )


@tool("get_visible_jira_projects")
async def get_visible_jira_projects(
    expand: str = "description,lead,issueTypes",
    max_results: int = 100,
    start_at: int = 0
) -> ToolResult:
    """Get visible Jira projects with filtering options.

    Args:
        expand: Comma-separated fields to expand (e.g., "description,lead,issueTypes")
        max_results: Maximum number of projects to return (default 100)
        start_at: Starting index for pagination (default 0)

    Returns:
        ToolResult: List of visible projects
    """
    auth_manager = AtlassianAuthManager()
    
    if not auth_manager.jira_base_url:
        return ToolResult(
            success=False,
            result={"error": "Jira base URL not configured"}
        )
    
    try:
        url = f"{auth_manager.jira_base_url}/rest/api/3/project/search"
        
        params = {
            "maxResults": min(max(max_results, 1), 1000),
            "startAt": max(start_at, 0)
        }
        
        if expand:
            params["expand"] = expand

        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                params=params,
                headers=auth_manager.get_auth_headers(),
                timeout=30.0
            )
            response.raise_for_status()
            
            projects_data = response.json()
            
            return ToolResult(
                success=True,
                result={
                    "total": projects_data.get("total", 0),
                    "projects": projects_data.get("values", []),
                    "start_at": projects_data.get("startAt", 0),
                    "max_results": projects_data.get("maxResults", 0)
                }
            )
            
    except Exception as e:
        logger.error(f"Error getting Jira projects: {e}")
        return ToolResult(
            success=False,
            result={"error": f"Failed to get projects: {str(e)}"}
        )


@tool("get_jira_project_issue_types_metadata")
async def get_jira_project_issue_types_metadata(
    project_key: str
) -> ToolResult:
    """Get issue types and metadata for a specific Jira project.

    Args:
        project_key: The Jira project key (e.g., "PROJ")

    Returns:
        ToolResult: Project issue types and creation metadata
    """
    auth_manager = AtlassianAuthManager()
    
    if not auth_manager.jira_base_url:
        return ToolResult(
            success=False,
            result={"error": "Jira base URL not configured"}
        )
    
    try:
        # Get project details with issue types
        project_url = f"{auth_manager.jira_base_url}/rest/api/3/project/{project_key}"
        create_meta_url = f"{auth_manager.jira_base_url}/rest/api/3/issue/createmeta"

        async with httpx.AsyncClient() as client:
            # Get project info
            project_response = await client.get(
                project_url,
                params={"expand": "issueTypes"},
                headers=auth_manager.get_auth_headers(),
                timeout=30.0
            )
            project_response.raise_for_status()
            project_data = project_response.json()
            
            # Get create metadata
            meta_response = await client.get(
                create_meta_url,
                params={"projectKeys": project_key, "expand": "projects.issuetypes.fields"},
                headers=auth_manager.get_auth_headers(),
                timeout=30.0
            )
            meta_response.raise_for_status()
            meta_data = meta_response.json()
            
            return ToolResult(
                success=True,
                result={
                    "project": {
                        "key": project_data.get("key"),
                        "name": project_data.get("name"),
                        "description": project_data.get("description"),
                        "lead": project_data.get("lead", {}).get("displayName")
                    },
                    "issue_types": project_data.get("issueTypes", []),
                    "create_metadata": meta_data.get("projects", [])
                }
            )
            
    except Exception as e:
        logger.error(f"Error getting Jira project metadata for {project_key}: {e}")
        return ToolResult(
            success=False,
            result={"error": f"Failed to get project metadata: {str(e)}"}
        )


# ============================================================================
# CONFLUENCE TOOLS
# ============================================================================

@tool("get_confluence_page")
async def get_confluence_page(
    page_id: str,
    expand: str = "body.storage,version,space,ancestors"
) -> ToolResult:
    """Get a Confluence page with content and metadata.

    Args:
        page_id: The Confluence page ID
        expand: Comma-separated fields to expand (e.g., "body.storage,version,space")

    Returns:
        ToolResult: Page content and metadata
    """
    auth_manager = AtlassianAuthManager()
    
    if not auth_manager.confluence_base_url:
        return ToolResult(
            success=False,
            result={"error": "Confluence base URL not configured"}
        )
    
    try:
        url = f"{auth_manager.confluence_base_url}/wiki/rest/api/content/{page_id}"
        params = {}
        
        if expand:
            params["expand"] = expand

        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                params=params,
                headers=auth_manager.get_auth_headers(),
                timeout=30.0
            )
            response.raise_for_status()
            
            page_data = response.json()
            
            return ToolResult(
                success=True,
                result={
                    "page": page_data,
                    "id": page_data.get("id"),
                    "title": page_data.get("title"),
                    "type": page_data.get("type"),
                    "space": page_data.get("space", {}).get("key"),
                    "version": page_data.get("version", {}).get("number")
                }
            )
            
    except Exception as e:
        logger.error(f"Error getting Confluence page {page_id}: {e}")
        return ToolResult(
            success=False,
            result={"error": f"Failed to get page: {str(e)}"}
        )


@tool("create_confluence_page")
async def create_confluence_page(
    space_key: str,
    title: str,
    content: str,
    parent_id: Optional[str] = None
) -> ToolResult:
    """Create a new Confluence page.

    Args:
        space_key: The Confluence space key
        title: Page title
        content: Page content (HTML format)
        parent_id: Parent page ID (optional)

    Returns:
        ToolResult: Created page details
    """
    auth_manager = AtlassianAuthManager()
    
    if not auth_manager.confluence_base_url:
        return ToolResult(
            success=False,
            result={"error": "Confluence base URL not configured"}
        )
    
    try:
        url = f"{auth_manager.confluence_base_url}/wiki/rest/api/content"
        
        # Build page payload
        payload = {
            "type": "page",
            "title": title,
            "space": {"key": space_key},
            "body": {
                "storage": {
                    "value": content,
                    "representation": "storage"
                }
            }
        }
        
        if parent_id:
            payload["ancestors"] = [{"id": parent_id}]

        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json=payload,
                headers=auth_manager.get_auth_headers(),
                timeout=30.0
            )
            response.raise_for_status()
            
            result_data = response.json()
            
            return ToolResult(
                success=True,
                result={
                    "page_id": result_data.get("id"),
                    "title": result_data.get("title"),
                    "space": result_data.get("space", {}).get("key"),
                    "url": f"{auth_manager.confluence_base_url}{result_data.get('_links', {}).get('webui')}",
                    "message": f"Successfully created page '{title}'"
                }
            )
            
    except Exception as e:
        logger.error(f"Error creating Confluence page: {e}")
        return ToolResult(
            success=False,
            result={"error": f"Failed to create page: {str(e)}"}
        )


@tool("update_confluence_page")
async def update_confluence_page(
    page_id: str,
    title: Optional[str] = None,
    content: Optional[str] = None,
    version_number: Optional[int] = None
) -> ToolResult:
    """Update an existing Confluence page.

    Args:
        page_id: The Confluence page ID to update
        title: New page title (optional)
        content: New page content in HTML format (optional)
        version_number: Current version number (will be auto-detected if not provided)

    Returns:
        ToolResult: Update result
    """
    auth_manager = AtlassianAuthManager()
    
    if not auth_manager.confluence_base_url:
        return ToolResult(
            success=False,
            result={"error": "Confluence base URL not configured"}
        )
    
    try:
        url = f"{auth_manager.confluence_base_url}/wiki/rest/api/content/{page_id}"
        
        async with httpx.AsyncClient() as client:
            # Get current page version if not provided
            if version_number is None:
                current_response = await client.get(
                    url,
                    params={"expand": "version"},
                    headers=auth_manager.get_auth_headers(),
                    timeout=30.0
                )
                current_response.raise_for_status()
                current_data = current_response.json()
                version_number = current_data.get("version", {}).get("number", 1)
            
            # Build update payload
            payload = {
                "version": {"number": version_number + 1}
            }
            
            if title is not None:
                payload["title"] = title
            
            if content is not None:
                payload["body"] = {
                    "storage": {
                        "value": content,
                        "representation": "storage"
                    }
                }

            response = await client.put(
                url,
                json=payload,
                headers=auth_manager.get_auth_headers(),
                timeout=30.0
            )
            response.raise_for_status()
            
            result_data = response.json()
            
            return ToolResult(
                success=True,
                result={
                    "page_id": result_data.get("id"),
                    "title": result_data.get("title"),
                    "version": result_data.get("version", {}).get("number"),
                    "url": f"{auth_manager.confluence_base_url}{result_data.get('_links', {}).get('webui')}",
                    "message": f"Successfully updated page {page_id}"
                }
            )
            
    except Exception as e:
        logger.error(f"Error updating Confluence page {page_id}: {e}")
        return ToolResult(
            success=False,
            result={"error": f"Failed to update page: {str(e)}"}
        )