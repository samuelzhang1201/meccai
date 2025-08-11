"""Shared dataclasses and typing protocols."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Protocol


@dataclass
class ToolCall:
    """Represents a tool call request."""

    id: str
    name: str
    arguments: dict[str, Any]


@dataclass
class ToolResult:
    """Represents a tool call result."""

    success: bool
    result: Any | None = None
    error: str | None = None
    id: str | None = None


@dataclass
class Message:
    """Represents a chat message."""

    role: str  # "user", "assistant", "system"
    content: str
    tool_calls: list[ToolCall] | None = None
    tool_call_id: str | None = None


@dataclass
class Conversation:
    """Represents a conversation context."""

    messages: list[Message]
    metadata: dict[str, Any] | None = None


class Tool(Protocol):
    """Protocol for tools that can be called by AI agents."""

    @property
    def name(self) -> str:
        """Tool name identifier."""
        ...

    @property
    def description(self) -> str:
        """Tool description for AI agents."""
        ...

    @property
    def parameters(self) -> dict[str, Any]:
        """Tool parameters schema (JSON Schema format)."""
        ...

    async def call(self, **kwargs: Any) -> ToolResult:
        """Execute the tool with given parameters."""
        ...


class ToolRegistry(Protocol):
    """Protocol for tool registries."""

    def register(self, tool: Tool) -> None:
        """Register a tool."""
        ...

    def get_tool(self, name: str) -> Tool | None:
        """Get a tool by name."""
        ...

    def list_tools(self) -> list[Tool]:
        """List all registered tools."""
        ...


class AIProvider(ABC):
    """Abstract base class for AI providers."""

    @abstractmethod
    async def generate_response(
        self,
        conversation: Conversation,
        tools: list[Tool] | None = None,
    ) -> Message:
        """Generate a response from the AI provider."""
        pass

    @abstractmethod
    async def call_tool(
        self,
        tool_call: ToolCall,
        available_tools: list[Tool],
    ) -> ToolResult:
        """Execute a tool call."""
        pass


@dataclass
class MCPServer:
    """Represents an MCP server configuration."""

    name: str
    command: str
    args: list[str]
    env: dict[str, str] | None = None
    description: str | None = None
    timeout: int = 30


@dataclass
class MCPEndpoint:
    """Represents an MCP HTTP endpoint."""

    name: str
    url: str
    headers: dict[str, str] | None = None
    timeout: int = 30


@dataclass
class AgentDecision:
    """Agent decision about task completion and handoff."""

    continue_chain: bool  # True = continue to next agent, False = stop here
    reason: str  # Explanation for the decision
    confidence: float = 1.0  # 0-1 confidence in the decision


@dataclass
class AgentResponse:
    """Extended response structure with agent decision."""

    message: Message  # The actual response content
    decision: AgentDecision  # Whether to continue the handoff chain
    agent_name: str  # Name of the agent that provided this response
