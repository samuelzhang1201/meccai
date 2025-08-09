"""Tableau REST API tools for data visualization and reporting."""

import base64
import xml.etree.ElementTree as ET
from typing import Any
from urllib.parse import urljoin

import httpx

from meccaai.core.config import settings
from meccaai.core.logging import get_logger
from meccaai.core.tool_base import tool
from meccaai.core.types import ToolResult

logger = get_logger(__name__)


class TableauAuthManager:
    """Manages Tableau authentication sessions."""

    def __init__(self):
        self.server_url = settings.tableau.server_url
        self.site_content_url = settings.tableau.site_content_url
        self.token_name = settings.tableau.token_name
        self.token_value = settings.tableau_token_value
        self.api_version = settings.tableau.api_version
        self.session_token: str | None = None
        self.site_id: str | None = None
        self.user_id: str | None = None

    async def sign_in(self) -> dict[str, Any]:
        """Sign in to Tableau Server and get session token."""
        if not self.token_value:
            raise ValueError(
                "Tableau token value not configured. Please set TABLEAU_TOKEN_VALUE environment variable."
            )

        signin_url = urljoin(self.server_url, f"/api/{self.api_version}/auth/signin")
        
        logger.info(f"Signing in to Tableau Server: {signin_url}")
        logger.debug(f"Using token name: {self.token_name}, site: {self.site_content_url}")

        # Use XML format as required by Tableau REST API
        signin_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<tsRequest>
    <credentials personalAccessTokenName="{self.token_name}" personalAccessTokenSecret="{self.token_value}">
        <site contentUrl="{self.site_content_url}" />
    </credentials>
</tsRequest>"""

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    signin_url,
                    content=signin_xml,
                    headers={"Content-Type": "application/xml"},
                )
                response.raise_for_status()
                
                # Parse XML response
                root = ET.fromstring(response.text)
                logger.debug(f"XML Response: {response.text[:200]}...")
                
                # Define namespace for Tableau API
                ns = {"ts": "http://tableau.com/api"}
                
                # Find credentials element with correct namespace
                credentials = root.find("ts:credentials", ns)
                if credentials is None:
                    logger.error(f"Could not find credentials in XML: {response.text}")
                    raise ValueError("Could not find credentials in response")
                
                # Get session token from credentials attributes
                self.session_token = credentials.get("token")
                logger.debug(f"Session token: {self.session_token[:10] if self.session_token else None}...")
                
                # Find site and user elements as children of credentials
                site = credentials.find("ts:site", ns)
                user = credentials.find("ts:user", ns)
                
                if site is not None:
                    self.site_id = site.get("id")
                    logger.debug(f"Site ID: {self.site_id}")
                else:
                    logger.error("Site element not found in credentials")
                    
                if user is not None:
                    self.user_id = user.get("id")
                    logger.debug(f"User ID: {self.user_id}")
                else:
                    logger.warning("User element not found in credentials")
                    # If user ID is not in sign-in response, we'll get it separately
                
                logger.info("Successfully signed in to Tableau Server")
                return {
                    "token": self.session_token,
                    "site_id": self.site_id,
                    "user_id": self.user_id
                }
        except httpx.HTTPStatusError as e:
            logger.error(f"Tableau authentication failed: {e.response.status_code} - {e.response.text}")
            raise ValueError(f"Tableau authentication failed: {e.response.status_code}. Check your token and site settings.")

    async def sign_out(self) -> bool:
        """Sign out from Tableau Server."""
        if not self.session_token:
            return True

        signout_url = urljoin(self.server_url, f"/api/{self.api_version}/auth/signout")

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    signout_url,
                    headers={
                        "X-Tableau-Auth": self.session_token,
                        "Content-Type": "application/json",
                    },
                )
                response.raise_for_status()

            self.session_token = None
            self.site_id = None
            self.user_id = None
            logger.info("Successfully signed out from Tableau Server")
            return True

        except Exception as e:
            logger.error(f"Error signing out: {e}")
            return False

    def get_auth_headers(self) -> dict[str, str]:
        """Get authentication headers for API requests."""
        if not self.session_token:
            raise ValueError("Not signed in to Tableau Server")

        return {
            "X-Tableau-Auth": self.session_token,
            "Accept": "application/xml",
        }

    async def get_current_user(self) -> str | None:
        """Get the current user's ID."""
        if not self.session_token or not self.site_id:
            return None
            
        # Get current user via "users/current" endpoint
        current_user_url = urljoin(
            self.server_url,
            f"/api/{self.api_version}/sites/{self.site_id}/users/current"
        )
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    current_user_url,
                    headers=self.get_auth_headers()
                )
                response.raise_for_status()
                
                # Parse XML response
                root = ET.fromstring(response.text)
                ns = {"ts": "http://tableau.com/api"}
                user = root.find(".//ts:user", ns) or root.find(".//user")
                
                if user is not None:
                    user_id = user.get("id")
                    logger.debug(f"Retrieved current user ID: {user_id}")
                    return user_id
                    
        except Exception as e:
            logger.error(f"Error getting current user: {e}")
            
        return None


@tool("list_all_pats")
async def list_all_personal_access_tokens() -> ToolResult:
    """List Personal Access Tokens (PATs) for the current user in the Tableau site.
    
    Note: This returns PATs for the authenticated user, not all users in the site.
    Only server administrators can list PATs for all users.

    Returns:
        ToolResult: List of user's PATs with details like name, creation date, and last used.
    """
    auth_manager = TableauAuthManager()

    try:
        # Sign in
        await auth_manager.sign_in()

        # Try different approaches to get user ID
        if not auth_manager.user_id:
            # Try to get current user ID
            auth_manager.user_id = await auth_manager.get_current_user()
        
        if auth_manager.user_id:
            # Use user-specific endpoint
            url = urljoin(
                auth_manager.server_url,
                f"/api/{auth_manager.api_version}/sites/{auth_manager.site_id}/users/{auth_manager.user_id}/personal-access-tokens",
            )
        else:
            # Fallback: try site-level endpoint (may not work, but worth trying)
            logger.warning("No user ID available, trying site-level PAT endpoint")
            url = urljoin(
                auth_manager.server_url,
                f"/api/{auth_manager.api_version}/sites/{auth_manager.site_id}/personal-access-tokens",
            )

        # Make the API request with pagination support
        all_tokens = []
        page_number = 1
        page_size = 100

        async with httpx.AsyncClient() as client:
            while True:
                params = {"pageSize": page_size, "pageNumber": page_number}

                response = await client.get(
                    url, params=params, headers=auth_manager.get_auth_headers()
                )
                response.raise_for_status()

                # Parse XML response 
                root = ET.fromstring(response.text)
                ns = {"ts": "http://tableau.com/api"}
                
                # Find personalAccessTokens element
                pats_element = root.find("ts:personalAccessTokens", ns)
                if pats_element is None:
                    logger.warning("No personalAccessTokens element found in response")
                    break
                
                # Find all personalAccessToken elements
                tokens = pats_element.findall("ts:personalAccessToken", ns)
                
                # Convert XML elements to dictionaries
                for token in tokens:
                    token_data = {}
                    token_data.update(token.attrib)  # Get all attributes
                    all_tokens.append(token_data)

                # Check pagination from the personalAccessTokens element
                total_available_attr = pats_element.get("totalAvailable")
                if total_available_attr:
                    total_available = int(total_available_attr)
                    if page_number * page_size >= total_available:
                        break
                else:
                    # No pagination info, assume this is all tokens
                    break

                page_number += 1

        # Sign out
        await auth_manager.sign_out()

        return ToolResult(
            success=True, result={"total_tokens": len(all_tokens), "tokens": all_tokens}
        )

    except Exception as e:
        await auth_manager.sign_out()  # Ensure cleanup
        logger.error(f"Error listing PATs: {e}")
        return ToolResult(success=False, error=str(e))


@tool("get_view")
async def get_view(view_id: str) -> ToolResult:
    """Get details of a specific Tableau view by its ID.

    Args:
        view_id: The unique identifier for the view

    Returns:
        ToolResult: View details including name, description, workbook info, etc.
    """
    auth_manager = TableauAuthManager()

    try:
        # Sign in
        await auth_manager.sign_in()

        # Build the API endpoint URL
        url = urljoin(
            auth_manager.server_url,
            f"/api/{auth_manager.api_version}/sites/{auth_manager.site_id}/views/{view_id}",
        )

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=auth_manager.get_auth_headers())
            response.raise_for_status()

            data = response.json()
            view = data["tsResponse"]["view"]

        # Sign out
        await auth_manager.sign_out()

        return ToolResult(success=True, result=view)

    except Exception as e:
        await auth_manager.sign_out()  # Ensure cleanup
        logger.error(f"Error getting view {view_id}: {e}")
        return ToolResult(success=False, error=str(e))


@tool("query_view_pdf")
async def query_view_pdf(
    view_id: str, filter_params: dict[str, Any] | None = None
) -> ToolResult:
    """Export a Tableau view as PDF.

    Args:
        view_id: The unique identifier for the view
        filter_params: Optional dictionary of filter parameters to apply

    Returns:
        ToolResult: Base64-encoded PDF content or download URL
    """
    auth_manager = TableauAuthManager()

    try:
        # Sign in
        await auth_manager.sign_in()

        # Build the API endpoint URL
        url = urljoin(
            auth_manager.server_url,
            f"/api/{auth_manager.api_version}/sites/{auth_manager.site_id}/views/{view_id}/pdf",
        )

        # Prepare query parameters
        params = {}
        if filter_params:
            for key, value in filter_params.items():
                params[f"vf_{key}"] = value

        async with httpx.AsyncClient(
            timeout=120.0
        ) as client:  # Longer timeout for PDF generation
            response = await client.get(
                url, params=params, headers=auth_manager.get_auth_headers()
            )
            response.raise_for_status()

            # Encode PDF content as base64 for JSON serialization
            pdf_content = base64.b64encode(response.content).decode("utf-8")

        # Sign out
        await auth_manager.sign_out()

        return ToolResult(
            success=True,
            result={
                "view_id": view_id,
                "pdf_size_bytes": len(response.content),
                "pdf_base64": pdf_content,
                "content_type": response.headers.get("content-type", "application/pdf"),
            },
        )

    except Exception as e:
        await auth_manager.sign_out()  # Ensure cleanup
        logger.error(f"Error exporting view {view_id} to PDF: {e}")
        return ToolResult(success=False, error=str(e))


@tool("list_views")
async def list_views(workbook_id: str | None = None) -> ToolResult:
    """List all views in the site, optionally filtered by workbook.

    Args:
        workbook_id: Optional workbook ID to filter views

    Returns:
        ToolResult: List of views with details
    """
    auth_manager = TableauAuthManager()

    try:
        # Sign in
        await auth_manager.sign_in()

        # Build the API endpoint URL
        if workbook_id:
            url = urljoin(
                auth_manager.server_url,
                f"/api/{auth_manager.api_version}/sites/{auth_manager.site_id}/workbooks/{workbook_id}/views",
            )
        else:
            url = urljoin(
                auth_manager.server_url,
                f"/api/{auth_manager.api_version}/sites/{auth_manager.site_id}/views",
            )

        # Make the API request with pagination support
        all_views = []
        page_number = 1
        page_size = 100

        async with httpx.AsyncClient() as client:
            while True:
                params = {"pageSize": page_size, "pageNumber": page_number}

                response = await client.get(
                    url, params=params, headers=auth_manager.get_auth_headers()
                )
                response.raise_for_status()

                data = response.json()
                views = data["tsResponse"]["views"]["view"]

                if isinstance(views, list):
                    all_views.extend(views)
                elif views:  # Single view
                    all_views.append(views)

                # Check if there are more pages
                pagination = data["tsResponse"]["views"]["pagination"]
                total_available = int(pagination["totalAvailable"])

                if page_number * page_size >= total_available:
                    break

                page_number += 1

        # Sign out
        await auth_manager.sign_out()

        return ToolResult(
            success=True, result={"total_views": len(all_views), "views": all_views}
        )

    except Exception as e:
        await auth_manager.sign_out()  # Ensure cleanup
        logger.error(f"Error listing views: {e}")
        return ToolResult(success=False, error=str(e))
