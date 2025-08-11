"""Minimal MCP (Model Context Protocol) client implementation."""

import asyncio
import json
import subprocess
from typing import Any

import httpx

from meccaai.core.logging import get_logger
from meccaai.core.types import MCPEndpoint, MCPServer

logger = get_logger(__name__)


class MCPError(Exception):
    """MCP client error."""

    pass


class MCPClient:
    """MCP client for communicating with MCP servers."""

    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self._processes: dict[str, subprocess.Popen] = {}
        self._http_client = httpx.AsyncClient(timeout=timeout)
        self._request_id = 0

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.cleanup()

    async def cleanup(self):
        """Cleanup resources."""
        # Terminate processes
        for name, process in self._processes.items():
            try:
                process.terminate()
                await asyncio.sleep(0.1)
                if process.poll() is None:
                    process.kill()
                logger.info(f"Terminated MCP server: {name}")
            except Exception as e:
                logger.warning(f"Error terminating MCP server {name}: {e}")

        self._processes.clear()

        # Close HTTP client
        await self._http_client.aclose()

    async def start_server(self, server: MCPServer) -> bool:
        """Start an MCP server process."""
        try:
            import os

            env = os.environ.copy()
            if server.env:
                env.update(server.env)

            process = subprocess.Popen(
                [server.command] + server.args,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                text=True,
                bufsize=0,  # Unbuffered
            )

            self._processes[server.name] = process

            # Wait a bit for server to start
            await asyncio.sleep(0.5)
            logger.info(f"Started MCP server: {server.name}")
            return True

        except Exception as e:
            logger.error(f"Failed to start MCP server {server.name}: {e}")
            return False

    async def _initialize_server(self, server_name: str):
        """Initialize MCP server with proper handshake."""
        # Initialize the server
        await self.call_server_method(
            server_name,
            "initialize",
            {
                "protocolVersion": "2024-11-05",
                "capabilities": {"roots": {"listChanged": True}, "sampling": {}},
                "clientInfo": {"name": "meccaai", "version": "1.0.0"},
            },
        )

        # Send initialized notification (no response expected)
        await self._send_notification(server_name, "notifications/initialized")

    async def _send_notification(
        self,
        server_name: str,
        method: str,
        params: dict[str, Any] | None = None,
    ):
        """Send a notification to an MCP server (no response expected)."""
        process = self._processes.get(server_name)
        if not process:
            raise MCPError(f"Server {server_name} not started")

        notification = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {},
        }

        try:
            # Send notification
            notification_json = json.dumps(notification) + "\n"
            if process.stdin:
                process.stdin.write(notification_json)
                process.stdin.flush()
            else:
                raise MCPError("Server stdin not available")
        except Exception as e:
            raise MCPError(f"Failed to send notification: {e}") from e

    async def call_server_method(
        self,
        server_name: str,
        method: str,
        params: dict[str, Any] | None = None,
    ) -> Any:
        """Call a method on an MCP server via JSON-RPC."""
        process = self._processes.get(server_name)
        if not process:
            raise MCPError(f"Server {server_name} not started")

        self._request_id += 1
        request = {
            "jsonrpc": "2.0",
            "id": self._request_id,
            "method": method,
            "params": params or {},
        }

        try:
            # Send request
            request_json = json.dumps(request) + "\n"
            if process.stdin:
                process.stdin.write(request_json)
                process.stdin.flush()
            else:
                raise MCPError("Server stdin not available")

            # Read response with timeout
            if not process.stdout:
                raise MCPError("Server stdout not available")

            response_line = await asyncio.wait_for(
                asyncio.to_thread(process.stdout.readline), timeout=self.timeout
            )

            if not response_line.strip():
                raise MCPError(f"No response from server {server_name}")

            response = json.loads(response_line)

            if "error" in response:
                error_info = response["error"]
                error_msg = error_info.get("message", str(error_info))
                raise MCPError(f"Server error: {error_msg}")

            return response.get("result")

        except TimeoutError as e:
            raise MCPError(
                f"Timeout waiting for response from server {server_name}"
            ) from e
        except json.JSONDecodeError as e:
            raise MCPError(f"Invalid JSON response: {e}") from e
        except Exception as e:
            raise MCPError(f"Communication error: {e}") from e

    async def call_endpoint_method(
        self,
        endpoint: MCPEndpoint,
        method: str,
        params: dict[str, Any] | None = None,
    ) -> Any:
        """Call a method on an MCP HTTP endpoint."""
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params or {},
        }

        try:
            response = await self._http_client.post(
                endpoint.url,
                json=request,
                headers=endpoint.headers or {},
                timeout=endpoint.timeout,
            )
            response.raise_for_status()

            result = response.json()

            if "error" in result:
                raise MCPError(f"Endpoint error: {result['error']}")

            return result.get("result")

        except httpx.HTTPError as e:
            raise MCPError(f"HTTP error: {e}") from e
        except Exception as e:
            raise MCPError(f"Request error: {e}") from e

    async def list_tools(self, server_name: str) -> list[dict[str, Any]]:
        """List available tools from an MCP server."""
        try:
            result = await self.call_server_method(server_name, "tools/list")
            return result.get("tools", [])
        except Exception as e:
            logger.warning(f"Failed to list tools from {server_name}: {e}")
            return []

    async def call_tool(
        self,
        server_name: str,
        tool_name: str,
        arguments: dict[str, Any],
    ) -> Any:
        """Call a tool on an MCP server."""
        # Try to initialize server if not already done
        try:
            await self._initialize_server(server_name)
        except Exception:
            # If initialization fails, try the call anyway
            pass

        params = {
            "name": tool_name,
            "arguments": arguments,
        }

        return await self.call_server_method(server_name, "tools/call", params)


def load_mcp_servers_config(config_path: str) -> list[MCPServer]:
    """Load MCP servers configuration from JSON file."""
    try:
        with open(config_path) as f:
            config = json.load(f)

        servers = []
        mcp_servers = config.get("mcpServers", {})

        for name, server_config in mcp_servers.items():
            # Skip URL-based servers (like Zapier) - only handle command-based servers
            if "url" in server_config:
                continue

            if "command" not in server_config:
                logger.warning(f"Skipping server {name}: missing 'command' field")
                continue

            server = MCPServer(
                name=name,
                command=server_config["command"],
                args=server_config.get("args", []),
                env=server_config.get("env"),
                description=server_config.get("description"),
                timeout=server_config.get("timeout", 30),
            )
            servers.append(server)

        return servers

    except Exception as e:
        logger.error(f"Failed to load MCP servers config: {e}")
        return []
