"""Bedrock-compatible agents that work with AWS Bedrock models."""

from meccaai.adapters.bedrock.bedrock_runner import BedrockRunner
from meccaai.core.config import settings
from meccaai.core.logging import get_logger
from meccaai.core.types import Message, Tool

logger = get_logger(__name__)

# PII leak indicators for output guardrail
LEAK_INDICATORS = ["password", "secret", "confidential", "private"]


def check_pii_leak(content: str) -> bool:
    """Check if content contains PII leak indicators."""
    content_lower = content.lower()
    return any(indicator in content_lower for indicator in LEAK_INDICATORS)


def output_guardrail(content: str) -> str:
    """Apply output guardrail to check for PII leaks."""
    if check_pii_leak(content):
        logger.warning("PII leak detected in output, content redacted")
        return "Content has been redacted due to potential PII information."
    return content


class BedrockAgent:
    """Bedrock-compatible agent that mimics OpenAI Agent SDK interface."""

    def __init__(
        self,
        name: str,
        instructions: str,
        tools: list[Tool] | None = None,
        model: str | None = None,
        apply_guardrail: bool = False,
    ):
        """Initialize Bedrock agent."""
        self.name = name
        self.instructions = instructions
        self.tools = tools or []
        self.model = model or settings.models.bedrock.model
        self.apply_guardrail = apply_guardrail
        self.runner = BedrockRunner()

    async def run(self, user_message: str) -> str:
        """Run the agent with a user message."""
        # Prepare system message with instructions
        system_instructions = f"You are {self.name}. {self.instructions}"

        # Create messages
        messages = [
            Message(role="system", content=system_instructions),
            Message(role="user", content=user_message),
        ]

        # Run conversation
        result = await self.runner.run_conversation(
            messages=messages,
            tools=self.tools,
            model=self.model,
            agent=self.name,
        )

        # Apply guardrail if enabled
        if self.apply_guardrail:
            result.content = output_guardrail(result.content)

        return result.content

    def as_tool(self, tool_name: str, tool_description: str) -> Tool:
        """Convert this agent to a tool (simplified version)."""
        from meccaai.core.tool_base import BaseTool, ToolResult

        class AgentTool(BaseTool):
            def __init__(self, agent: BedrockAgent, name: str, description: str):
                async def agent_func(input: str) -> ToolResult:
                    try:
                        result = await agent.run(input)
                        return ToolResult(
                            success=True,
                            result=result,
                            error=None,
                        )
                    except Exception as e:
                        return ToolResult(
                            success=False,
                            result=None,
                            error=str(e),
                        )

                parameters_schema = {
                    "type": "object",
                    "properties": {
                        "input": {
                            "type": "string",
                            "description": "The input message for the agent",
                        }
                    },
                    "required": ["input"],
                }

                super().__init__(name, description, agent_func, parameters_schema)
                self.agent = agent

        return AgentTool(self, tool_name, tool_description)


class BedrockAgentSystem:
    """Bedrock agent system that manages multiple agents."""

    def __init__(self):
        """Initialize the Bedrock agent system."""
        self.agents: dict[str, BedrockAgent] = {}
        self.runner = BedrockRunner()

    def add_agent(self, agent: BedrockAgent):
        """Add an agent to the system."""
        self.agents[agent.name] = agent

    def list_agents(self) -> dict[str, str]:
        """List all available agents."""
        return {name: agent.instructions[:100] for name, agent in self.agents.items()}

    async def process_request(
        self,
        messages: list[Message],
        agent: str | None = None,
        workflow: bool = False,
    ) -> Message:
        """Process a request using the specified agent."""
        # Extract the user message
        user_message = messages[-1].content if messages else ""

        # Select agent
        if agent and agent in self.agents:
            selected_agent = self.agents[agent]
        else:
            # Default to first available agent or create a simple one
            if self.agents:
                selected_agent = next(iter(self.agents.values()))
            else:
                selected_agent = BedrockAgent(
                    name="default",
                    instructions="You are a helpful AI assistant.",
                    tools=[],
                )

        try:
            result = await selected_agent.run(user_message)
            return Message(role="assistant", content=result)
        except Exception as e:
            logger.error(f"Error processing request: {e}")
            return Message(
                role="assistant",
                content=f"I encountered an error: {str(e)}",
            )
