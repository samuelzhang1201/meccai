"""OpenAI-based application entry point."""

import asyncio

import click

from meccaai.adapters.openai_sdk.runner import OpenAIRunner
from meccaai.core.config import settings
from meccaai.core.logging import get_logger, setup_logging
from meccaai.core.tool_registry import discover_tools_in_module, get_registry
from meccaai.core.types import Message

logger = get_logger(__name__)


class MeccaAIApp:
    """Main MeccaAI application using OpenAI SDK."""

    def __init__(self):
        self.runner = OpenAIRunner()
        self.registry = get_registry()
        self._initialized = False

    async def initialize(self):
        """Initialize the application."""
        if self._initialized:
            return

        # Setup logging
        setup_logging()
        logger.info("Initializing MeccaAI application")

        # Discover and register tools
        if settings.tools.auto_discover:
            for module_path in settings.tools.registry_paths:
                discover_tools_in_module(module_path, self.registry)

        # TODO: Initialize MCP clients if enabled
        if settings.tools.mcp_enabled:
            logger.info("MCP support enabled (not yet implemented)")

        self._initialized = True
        logger.info(
            f"Application initialized with {len(self.registry.list_tools())} tools"
        )

    async def run(self, prompt: str) -> str:
        """Run a single prompt through the AI system."""
        await self.initialize()

        messages = [Message(role="user", content=prompt)]
        response = await self.runner.run_conversation(messages)
        return response.content

    async def chat(self):
        """Interactive chat mode."""
        await self.initialize()

        print("MeccaAI Chat - Type 'quit' to exit")
        print(f"Available tools: {[tool.name for tool in self.registry.list_tools()]}")
        print()

        messages: list[Message] = []

        while True:
            try:
                user_input = input("You: ").strip()
                if user_input.lower() in ["quit", "exit", "q"]:
                    break

                if not user_input:
                    continue

                messages.append(Message(role="user", content=user_input))

                print("Assistant: ", end="", flush=True)
                response = await self.runner.run_conversation(messages)
                print(response.content)
                print()

                messages.append(response)

            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"Error: {e}")


def create_app() -> MeccaAIApp:
    """Create a MeccaAI application instance."""
    return MeccaAIApp()


@click.command()
@click.option("--prompt", "-p", help="Single prompt to run")
@click.option("--chat", "-c", is_flag=True, help="Interactive chat mode")
def main(prompt: str | None = None, chat: bool = False):
    """MeccaAI CLI application."""
    app = create_app()

    if prompt:
        # Single prompt mode
        async def run_prompt():
            result = await app.run(prompt)
            print(result)

        asyncio.run(run_prompt())

    elif chat:
        # Interactive chat mode
        asyncio.run(app.chat())

    else:
        # Default to chat mode
        asyncio.run(app.chat())


if __name__ == "__main__":
    main()
