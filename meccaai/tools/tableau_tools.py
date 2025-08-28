"""Tableau REST API tools for data visualization and reporting."""

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
        logger.debug(
            f"Using token name: {self.token_name}, site: {self.site_content_url}"
        )

        # Use JSON format for Tableau REST API authentication
        signin_payload = {
            "credentials": {
                "personalAccessTokenName": self.token_name,
                "personalAccessTokenSecret": self.token_value,
                "site": {"contentUrl": self.site_content_url},
            }
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    signin_url,
                    json=signin_payload,
                    headers={
                        "Content-Type": "application/json",
                        "Accept": "application/json",
                    },
                )

                # Log response status code
                logger.info(
                    f"Tableau API signin response status: {response.status_code}"
                )
                response.raise_for_status()

                # Parse JSON response
                data = response.json()
                logger.debug(f"JSON Response: {str(data)[:200]}...")

                # Extract credentials from JSON response
                credentials = data.get("credentials", {})
                if not credentials:
                    logger.error(f"Could not find credentials in JSON: {data}")
                    raise ValueError("Could not find credentials in response")

                # Get session token from credentials
                self.session_token = credentials.get("token")
                logger.debug(
                    f"Session token: {self.session_token[:10] if self.session_token else None}..."
                )

                # Get site and user information
                site = credentials.get("site", {})
                user = credentials.get("user", {})

                if site:
                    self.site_id = site.get("id")
                    logger.debug(f"Site ID: {self.site_id}")
                else:
                    logger.error("Site element not found in credentials")

                if user:
                    self.user_id = user.get("id")
                    logger.debug(f"User ID: {self.user_id}")
                else:
                    logger.warning("User element not found in credentials")
                    # If user ID is not in sign-in response, we'll get it separately

                logger.info("Successfully signed in to Tableau Server")
                return {
                    "token": self.session_token,
                    "site_id": self.site_id,
                    "user_id": self.user_id,
                }
        except httpx.HTTPStatusError as e:
            logger.error(
                f"Tableau authentication failed: {e.response.status_code} - {e.response.text}"
            )
            raise ValueError(
                f"Tableau authentication failed: {e.response.status_code}. Check your token and site settings."
            ) from e

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

                # Log response status code
                logger.info(
                    f"Tableau API signout response status: {response.status_code}"
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
            "Accept": "application/json",
        }

    async def get_current_user(self) -> str | None:
        """Get the current user's ID."""
        if not self.session_token or not self.site_id:
            return None

        # Get current user via "users/current" endpoint
        current_user_url = urljoin(
            self.server_url,
            f"/api/{self.api_version}/sites/{self.site_id}/users/current",
        )

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    current_user_url, headers=self.get_auth_headers()
                )

                # Log response status code
                logger.info(
                    f"Tableau API get_current_user response status: {response.status_code}"
                )
                response.raise_for_status()

                # Parse JSON response
                data = response.json()
                user = data.get("user", {})

                if user:
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

        # Configure timeout
        timeout = httpx.Timeout(60.0)  # 60 second timeout
        async with httpx.AsyncClient(timeout=timeout) as client:
            while True:
                params = {"pageSize": page_size, "pageNumber": page_number}

                response = await client.get(
                    url, params=params, headers=auth_manager.get_auth_headers()
                )

                # Log response status code
                logger.info(
                    f"Tableau API list_pats response status: {response.status_code}"
                )
                response.raise_for_status()

                # Parse JSON response
                data = response.json()

                # Find personalAccessTokens data
                pats_data = data.get("personalAccessTokens", {})
                if not pats_data:
                    logger.warning("No personalAccessTokens data found in response")
                    break

                # Find all personalAccessToken elements
                tokens = pats_data.get("personalAccessToken", [])
                if not isinstance(tokens, list):
                    tokens = [tokens] if tokens else []

                # Add token data to results
                all_tokens.extend(tokens)

                # Check pagination
                pagination = pats_data.get("pagination", {})
                total_available = int(pagination.get("totalAvailable", 0))
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
        raise e


# User Management Tools


@tool("add_user_to_site")
async def add_user_to_site(
    username: str,
    site_role: str = "Viewer",
    auth_setting: str = "ServerDefault",
) -> ToolResult:
    """Add a user to the site.

    Args:
        username: The username for the new user
        site_role: Site role for the user (Creator, Explorer, Viewer, etc.)
        auth_setting: Authentication setting (ServerDefault, SAML, etc.)

    Returns:
        ToolResult: Details of the created user
    """
    auth_manager = TableauAuthManager()

    try:
        # Sign in
        await auth_manager.sign_in()

        # Build the API endpoint URL
        url = urljoin(
            auth_manager.server_url,
            f"/api/{auth_manager.api_version}/sites/{auth_manager.site_id}/users",
        )

        # Prepare JSON payload
        user_payload = {
            "user": {
                "name": username,
                "siteRole": site_role,
                "authSetting": auth_setting,
            }
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json=user_payload,
                headers={
                    **auth_manager.get_auth_headers(),
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
            )

            # Log response status code
            logger.info(
                f"Tableau API add_user_to_site response status: {response.status_code}"
            )
            response.raise_for_status()

            # Parse JSON response
            data = response.json()
            user_element = data.get("user", {})

            if user_element:
                user_data = {
                    "id": user_element.get("id"),
                    "name": user_element.get("name"),
                    "siteRole": user_element.get("siteRole"),
                    "authSetting": user_element.get("authSetting"),
                }
            else:
                user_data = {"message": "User created successfully"}

        # Sign out
        await auth_manager.sign_out()

        return ToolResult(success=True, result=user_data)

    except Exception as e:
        await auth_manager.sign_out()  # Ensure cleanup
        logger.error(f"Error adding user {username} to site: {e}")
        raise e


@tool("get_users_on_site")
async def get_users_on_site(
    filter_expression: str = "",
    sort_expression: str = "",
    fields: str = "_default_",
    page_size: int = 100,
) -> ToolResult:
    """Get users on the site with optional filtering and sorting.

    Args:
        filter_expression: Filter users (e.g., "siteRole:eq:Viewer" or "lastLogin:gte:2023-01-01T00:00:00Z")
        sort_expression: Sort users (e.g., "name:asc" or "lastLogin:desc")
        fields: Fields to return (_default_, _all_, or specific fields like "id,name,siteRole")
        page_size: Number of users per page (1-1000, default 100)

    Returns:
        ToolResult: List of users with their details
    """
    auth_manager = TableauAuthManager()

    try:
        # Sign in
        await auth_manager.sign_in()

        # Build the API endpoint URL
        url = urljoin(
            auth_manager.server_url,
            f"/api/{auth_manager.api_version}/sites/{auth_manager.site_id}/users",
        )

        # Make the API request with pagination support
        all_users = []
        page_number = 1

        # Build query parameters
        params = {
            "pageSize": min(max(page_size, 1), 1000),  # Validate page_size range
            "pageNumber": page_number,
        }

        if filter_expression:
            params["filter"] = filter_expression
        if sort_expression:
            params["sort"] = sort_expression
        # Skip fields parameter for users API as it's causing 400 errors with some field names
        # The API returns all available fields by default anyway
        # if fields and fields != "_default_":
        #     params["fields"] = fields

        # Configure timeout
        timeout = httpx.Timeout(60.0)  # 60 second timeout
        async with httpx.AsyncClient(timeout=timeout) as client:
            while True:
                params["pageNumber"] = page_number

                response = await client.get(
                    url, params=params, headers=auth_manager.get_auth_headers()
                )

                # Log response status code
                logger.info(f"Tableau API response status: {response.status_code}")
                response.raise_for_status()

                data = response.json()

                # Extract users data
                users_data = data.get("users", {})
                if "user" in users_data:
                    users = users_data["user"]
                    if isinstance(users, list):
                        all_users.extend(users)
                    elif users:  # Single user
                        all_users.append(users)

                # Check pagination from top level
                pagination = data.get("pagination", {})
                total_available = int(pagination.get("totalAvailable", 0))

                if page_number * page_size >= total_available:
                    break

                page_number += 1

        # Sign out
        await auth_manager.sign_out()

        return ToolResult(
            success=True, result={"total_users": len(all_users), "users": all_users}
        )

    except Exception as e:
        await auth_manager.sign_out()  # Ensure cleanup
        logger.error(f"Error getting users on site: {e}")
        raise e


@tool("get_users_in_group")
async def get_users_in_group(group_id: str) -> ToolResult:
    """Get all users in a specific group.

    Args:
        group_id: The ID of the group

    Returns:
        ToolResult: List of users in the group
    """
    auth_manager = TableauAuthManager()

    try:
        # Sign in
        await auth_manager.sign_in()

        # Build the API endpoint URL
        url = urljoin(
            auth_manager.server_url,
            f"/api/{auth_manager.api_version}/sites/{auth_manager.site_id}/groups/{group_id}/users",
        )

        # Make the API request with pagination support
        all_users = []
        page_number = 1
        page_size = 100  # Smaller page size to avoid timeout

        # Configure timeout
        timeout = httpx.Timeout(60.0)  # 60 second timeout
        async with httpx.AsyncClient(timeout=timeout) as client:
            while True:
                params = {"pageSize": page_size, "pageNumber": page_number}

                response = await client.get(
                    url, params=params, headers=auth_manager.get_auth_headers()
                )

                # Log response status code
                logger.info(f"Tableau API response status: {response.status_code}")
                response.raise_for_status()

                data = response.json()

                # Extract users data
                users_data = data.get("users", {})
                if "user" in users_data:
                    users = users_data["user"]
                    if isinstance(users, list):
                        all_users.extend(users)
                    elif users:  # Single user
                        all_users.append(users)

                # Check pagination from top level
                pagination = data.get("pagination", {})
                total_available = int(pagination.get("totalAvailable", 0))

                if page_number * page_size >= total_available:
                    break

                page_number += 1

        # Sign out
        await auth_manager.sign_out()

        return ToolResult(
            success=True,
            result={
                "group_id": group_id,
                "total_users": len(all_users),
                "users": all_users,
            },
        )

    except Exception as e:
        await auth_manager.sign_out()  # Ensure cleanup
        logger.error(f"Error getting users in group {group_id}: {e}")
        raise e


@tool("get_group_set")
async def get_group_set(
    filter_expression: str = "",
    sort_expression: str = "",
    fields: str = "_default_",
    page_size: int = 100,
) -> ToolResult:
    """Get groups on the site with optional filtering and sorting.

    Args:
        filter_expression: Filter groups (e.g., "name:has:Admin" or "domainName:eq:local")
        sort_expression: Sort groups (e.g., "name:asc" or "createdAt:desc")
        fields: Fields to return (_default_, _all_, or specific fields like "id,name,domainName")
        page_size: Number of groups per page (1-1000, default 100)

    Returns:
        ToolResult: List of groups with their details
    """
    auth_manager = TableauAuthManager()

    try:
        # Sign in
        await auth_manager.sign_in()

        # Build the API endpoint URL
        url = urljoin(
            auth_manager.server_url,
            f"/api/{auth_manager.api_version}/sites/{auth_manager.site_id}/groups",
        )

        # Make the API request with pagination support
        all_groups = []
        page_number = 1

        # Build query parameters
        params = {
            "pageSize": min(max(page_size, 1), 1000),  # Validate page_size range
            "pageNumber": page_number,
        }

        if filter_expression:
            params["filter"] = filter_expression
        if sort_expression:
            params["sort"] = sort_expression
        if fields and fields != "_default_":
            params["fields"] = fields

        # Configure timeout
        timeout = httpx.Timeout(60.0)  # 60 second timeout
        async with httpx.AsyncClient(timeout=timeout) as client:
            while True:
                params["pageNumber"] = page_number

                response = await client.get(
                    url, params=params, headers=auth_manager.get_auth_headers()
                )

                # Log response status code
                logger.info(f"Tableau API response status: {response.status_code}")
                response.raise_for_status()

                data = response.json()

                # Extract groups data
                groups_data = data.get("groups", {})
                if "group" in groups_data:
                    groups = groups_data["group"]
                    if isinstance(groups, list):
                        all_groups.extend(groups)
                    elif groups:  # Single group
                        all_groups.append(groups)

                # Check pagination from top level
                pagination = data.get("pagination", {})
                total_available = int(pagination.get("totalAvailable", 0))

                if page_number * page_size >= total_available:
                    break

                page_number += 1

        # Sign out
        await auth_manager.sign_out()

        return ToolResult(
            success=True, result={"total_groups": len(all_groups), "groups": all_groups}
        )

    except Exception as e:
        await auth_manager.sign_out()  # Ensure cleanup
        logger.error(f"Error getting group set: {e}")
        raise e


@tool("update_user")
async def update_user(
    user_id: str,
    site_role: str | None = None,
    auth_setting: str | None = None,
    full_name: str | None = None,
    email: str | None = None,
) -> ToolResult:
    """Update a user on the site.

    Args:
        user_id: The ID of the user to update
        site_role: New site role for the user (optional)
        auth_setting: New authentication setting (optional)
        full_name: New full name for the user (optional)
        email: New email address for the user (optional)

    Returns:
        ToolResult: Updated user details
    """
    auth_manager = TableauAuthManager()

    try:
        # Sign in
        await auth_manager.sign_in()

        # Build the API endpoint URL
        url = urljoin(
            auth_manager.server_url,
            f"/api/{auth_manager.api_version}/sites/{auth_manager.site_id}/users/{user_id}",
        )

        # Prepare JSON payload with only provided fields
        user_data = {}
        if site_role:
            user_data["siteRole"] = site_role
        if auth_setting:
            user_data["authSetting"] = auth_setting
        if full_name:
            user_data["fullName"] = full_name
        if email:
            user_data["email"] = email

        if not user_data:
            raise ValueError("No fields provided to update")

        user_payload = {"user": user_data}

        async with httpx.AsyncClient() as client:
            response = await client.put(
                url,
                json=user_payload,
                headers={
                    **auth_manager.get_auth_headers(),
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
            )

            # Log response status code
            logger.info(
                f"Tableau API update_user response status: {response.status_code}"
            )
            response.raise_for_status()

            # Parse JSON response
            data = response.json()
            user_element = data.get("user", {})

            if user_element:
                user_data = {
                    "id": user_element.get("id"),
                    "name": user_element.get("name"),
                    "siteRole": user_element.get("siteRole"),
                    "authSetting": user_element.get("authSetting"),
                    "fullName": user_element.get("fullName"),
                    "email": user_element.get("email"),
                }
            else:
                user_data = {"message": "User updated successfully"}

        # Sign out
        await auth_manager.sign_out()

        return ToolResult(success=True, result=user_data)

    except Exception as e:
        await auth_manager.sign_out()  # Ensure cleanup
        logger.error(f"Error updating user {user_id}: {e}")
        raise e


# Content Management Tools


@tool("get_content_usage")
async def get_content_usage(
    content_items: list[dict[str, str]] | None = None,
) -> ToolResult:
    """Get content usage statistics using the BatchGetUsage endpoint.

    Note: This endpoint is only available for Tableau Cloud (API 3.17+), not Tableau Server.
    Gets usage metrics for workbooks, views, data sources, and flows.

    Args:
        content_items: List of content items to get usage for. Each item should have
                      'content_type' (workbook/view/datasource/flow) and 'luid' keys.
                      If None, will attempt to get general usage statistics.

    Returns:
        ToolResult: Content usage statistics including views, favorites, and access metrics
    """
    auth_manager = TableauAuthManager()

    try:
        # Sign in
        await auth_manager.sign_in()

        # Build the API endpoint URL for the BatchGetUsage endpoint
        # This is the new content exploration endpoint format (note: uses /api/- instead of version)
        url = urljoin(auth_manager.server_url, "/api/-/content/usage-stats")

        # Prepare request body based on the correct API format
        # The correct format is: {"content_items": [{"luid": "id", "type": "workbook"}]}
        if content_items:
            # Handle case where content_items might be passed as a JSON string from Bedrock
            if isinstance(content_items, str):
                try:
                    import json

                    content_items = json.loads(content_items)
                    logger.info(
                        f"Parsed content_items from JSON string: {len(content_items)} items"
                    )
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse content_items JSON string: {e}")
                    return ToolResult(
                        success=False,
                        result={"error": f"Invalid content_items JSON format: {e}"},
                    )

            # Format each content item properly for the API
            formatted_items = []
            for item in content_items:
                if isinstance(item, dict):
                    # Handle both contentType and type field names
                    content_type = item.get("contentType") or item.get(
                        "type", "workbook"
                    )
                    luid = item.get("luid") or item.get("id")

                    if luid:
                        formatted_items.append({"luid": luid, "type": content_type})

            if formatted_items:
                request_body = {"content_items": formatted_items}
            else:
                # If no valid items, return empty result immediately
                return ToolResult(
                    success=True,
                    result={
                        "message": "No valid content items provided for usage statistics",
                        "content_usage": {"content_items": []},
                    },
                )
        else:
            # If no content items provided, return empty result immediately
            return ToolResult(
                success=True,
                result={
                    "message": "No content items specified. Please provide workbook/view IDs to get usage statistics.",
                    "content_usage": {"content_items": []},
                },
            )

        # Configure timeout for potentially long-running request
        timeout = httpx.Timeout(120.0)  # 2 minute timeout

        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                url,
                json=request_body,
                headers={
                    **auth_manager.get_auth_headers(),
                    "Content-Type": "application/vnd.tableau.usagestats.v1.BatchGetUsageRequest+json",
                    "Accept": "application/vnd.tableau.usagestats.v1.ContentItemUsageStatsList+json",
                },
            )

            # Log response status code and details
            logger.info(
                f"Tableau API get_content_usage response status: {response.status_code}"
            )
            logger.debug(f"Request URL: {url}")
            logger.debug(f"Request body: {request_body}")

            # Accept both 200 and 201 status codes (API returns 201 Created)
            if response.status_code not in [200, 201]:
                logger.error(f"API Error Response: {response.text}")

            response.raise_for_status()

            # Parse JSON response
            data = response.json()

        # Sign out
        await auth_manager.sign_out()

        return ToolResult(success=True, result={"content_usage": data})

    except Exception as e:
        await auth_manager.sign_out()  # Ensure cleanup
        logger.error(f"Error getting content usage: {e}")
        raise e


@tool("get_datasources")
async def get_datasources(
    filter_expression: str = "",
    sort_expression: str = "",
    fields: str = "_default_",
    page_size: int = 100,
) -> ToolResult:
    """Get published data sources on the site with optional filtering and sorting.

    Args:
        filter_expression: Filter data sources (e.g., "name:has:Sales" or "updatedAt:gte:2023-01-01T00:00:00Z")
        sort_expression: Sort data sources (e.g., "name:asc" or "updatedAt:desc")
        fields: Fields to return (_default_, _all_, or specific fields like "id,name,updatedAt")
        page_size: Number of data sources per page (1-1000, default 100)

    Returns:
        ToolResult: List of published data sources with their details
    """
    auth_manager = TableauAuthManager()

    try:
        # Sign in
        await auth_manager.sign_in()

        # Build the API endpoint URL
        url = urljoin(
            auth_manager.server_url,
            f"/api/{auth_manager.api_version}/sites/{auth_manager.site_id}/datasources",
        )

        # Make the API request with pagination support
        all_datasources = []
        page_number = 1

        # Build query parameters
        params = {
            "pageSize": min(max(page_size, 1), 1000),  # Validate page_size range
            "pageNumber": page_number,
        }

        if filter_expression:
            params["filter"] = filter_expression
        if sort_expression:
            params["sort"] = sort_expression
        if fields and fields != "_default_":
            params["fields"] = fields

        # Configure timeout
        timeout = httpx.Timeout(60.0)  # 60 second timeout
        async with httpx.AsyncClient(timeout=timeout) as client:
            while True:
                params["pageNumber"] = page_number

                response = await client.get(
                    url, params=params, headers=auth_manager.get_auth_headers()
                )

                # Log response status code
                logger.info(
                    f"Tableau API get_datasources response status: {response.status_code}"
                )
                response.raise_for_status()

                data = response.json()

                # Extract datasources data
                datasources_data = data.get("datasources", {})
                if "datasource" in datasources_data:
                    datasources = datasources_data["datasource"]
                    if isinstance(datasources, list):
                        all_datasources.extend(datasources)
                    elif datasources:  # Single datasource
                        all_datasources.append(datasources)

                # Check pagination from top level
                pagination = data.get("pagination", {})
                total_available = int(pagination.get("totalAvailable", 0))

                if page_number * page_size >= total_available:
                    break

                page_number += 1

        # Sign out
        await auth_manager.sign_out()

        return ToolResult(
            success=True,
            result={
                "total_datasources": len(all_datasources),
                "datasources": all_datasources,
            },
        )

    except Exception as e:
        await auth_manager.sign_out()  # Ensure cleanup
        logger.error(f"Error getting datasources: {e}")
        raise e


@tool("get_workbooks")
async def get_workbooks(
    filter_expression: str = "",
    sort_expression: str = "",
    fields: str = "_default_",
    page_size: int = 100,
) -> ToolResult:
    """Get workbooks on the site with optional filtering and sorting.

    Args:
        filter_expression: Filter workbooks (e.g., "createdAt:gt:2023-01-01T00:00:00Z" or "ownerName:eq:john")
        sort_expression: Sort workbooks (e.g., "createdAt:desc" or "name:asc")
        fields: Fields to return (_default_, _all_, or specific fields like "id,name,owner,project")
        page_size: Number of workbooks per page (1-1000, default 100)

    Returns:
        ToolResult: List of workbooks with their details
    """
    auth_manager = TableauAuthManager()

    try:
        # Sign in
        await auth_manager.sign_in()

        # Build the API endpoint URL
        url = urljoin(
            auth_manager.server_url,
            f"/api/{auth_manager.api_version}/sites/{auth_manager.site_id}/workbooks",
        )

        # Make the API request with pagination support
        all_workbooks = []
        page_number = 1

        # Build query parameters
        params = {
            "pageSize": min(max(page_size, 1), 1000),  # Validate page_size range
            "pageNumber": page_number,
        }

        if filter_expression:
            params["filter"] = filter_expression
        if sort_expression:
            params["sort"] = sort_expression
        if fields and fields != "_default_":
            params["fields"] = fields

        # Configure timeout
        timeout = httpx.Timeout(60.0)  # 60 second timeout
        async with httpx.AsyncClient(timeout=timeout) as client:
            while True:
                params["pageNumber"] = page_number

                response = await client.get(
                    url, params=params, headers=auth_manager.get_auth_headers()
                )

                # Log response status code
                logger.info(
                    f"Tableau API get_workbooks response status: {response.status_code}"
                )
                response.raise_for_status()

                data = response.json()

                # Extract workbooks data
                workbooks_data = data.get("workbooks", {})
                if "workbook" in workbooks_data:
                    workbooks = workbooks_data["workbook"]
                    if isinstance(workbooks, list):
                        all_workbooks.extend(workbooks)
                    elif workbooks:  # Single workbook
                        all_workbooks.append(workbooks)

                # Check pagination from top level
                pagination = data.get("pagination", {})
                total_available = int(pagination.get("totalAvailable", 0))

                if page_number * page_size >= total_available:
                    break

                page_number += 1

        # Sign out
        await auth_manager.sign_out()

        return ToolResult(
            success=True,
            result={"total_workbooks": len(all_workbooks), "workbooks": all_workbooks},
        )

    except Exception as e:
        await auth_manager.sign_out()  # Ensure cleanup
        logger.error(f"Error getting workbooks: {e}")
        raise e


@tool("get_views_on_site")
async def get_views_on_site(
    filter_expression: str = "",
    sort_expression: str = "",
    fields: str = "_default_",
    page_size: int = 100,
) -> ToolResult:
    """Get views on the site with optional filtering and sorting.

    This can be used to get view LUIDs that can then be passed to get_content_usage.

    Args:
        filter_expression: Filter views (e.g., "workbookId:eq:abc123" or "viewUrlName:eq:Dashboard")
        sort_expression: Sort views (e.g., "createdAt:desc" or "name:asc")
        fields: Fields to return (_default_, _all_, or specific fields like "id,name,viewUrlName")
        page_size: Number of views per page (1-1000, default 100)

    Returns:
        ToolResult: List of views with their details including LUIDs
    """
    auth_manager = TableauAuthManager()

    try:
        # Sign in
        await auth_manager.sign_in()

        # Build the API endpoint URL
        url = urljoin(
            auth_manager.server_url,
            f"/api/{auth_manager.api_version}/sites/{auth_manager.site_id}/views",
        )

        # Make the API request with pagination support
        all_views = []
        page_number = 1

        # Build query parameters
        params = {
            "pageSize": min(max(page_size, 1), 1000),  # Validate page_size range
            "pageNumber": page_number,
        }

        if filter_expression:
            params["filter"] = filter_expression
        if sort_expression:
            params["sort"] = sort_expression
        if fields and fields != "_default_":
            params["fields"] = fields

        # Configure timeout
        timeout = httpx.Timeout(60.0)  # 60 second timeout
        async with httpx.AsyncClient(timeout=timeout) as client:
            while True:
                params["pageNumber"] = page_number

                response = await client.get(
                    url, params=params, headers=auth_manager.get_auth_headers()
                )

                # Log response status code
                logger.info(
                    f"Tableau API get_views_on_site response status: {response.status_code}"
                )
                response.raise_for_status()

                data = response.json()

                # Extract views data
                views_data = data.get("views", {})
                if "view" in views_data:
                    views = views_data["view"]
                    if isinstance(views, list):
                        all_views.extend(views)
                    elif views:  # Single view
                        all_views.append(views)

                # Check pagination from top level
                pagination = data.get("pagination", {})
                total_available = int(pagination.get("totalAvailable", 0))

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
        logger.error(f"Error getting views on site: {e}")
        raise e
