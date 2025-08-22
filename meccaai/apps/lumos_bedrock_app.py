"""Lumos AI application with AWS Bedrock support."""

import asyncio

import click

from meccaai.apps.lumos_bedrock_agents import LumosBedrockAgentSystem
from meccaai.core.logging import get_logger
from meccaai.core.types import Message

logger = get_logger(__name__)


@click.group(invoke_without_command=True)
@click.option("--chat", is_flag=True, help="Start interactive chat mode")
@click.pass_context
def cli(ctx, chat):
    """Lumos AI Multi-Agent System with AWS Bedrock."""
    if chat:
        # Start interactive chat mode
        asyncio.run(_interactive_chat())
        ctx.exit()
    elif ctx.invoked_subcommand is None:
        # Show help if no command and no --chat flag
        click.echo(ctx.get_help())


@cli.command()
@click.option(
    "--agent", "-a", help="Specific agent to use (data_analyst, data_manager, etc.)"
)
@click.option("--workflow", "-w", is_flag=True, help="Use orchestrated workflow")
@click.argument("message")
def chat(agent: str | None, workflow: bool, message: str):
    """Chat with the Lumos AI system using Bedrock models."""
    asyncio.run(_chat(agent, workflow, message))


@cli.command()
def list_agents():
    """List all available Bedrock agents."""
    system = LumosBedrockAgentSystem()
    agents = system.list_agents()

    click.echo("Available Bedrock Agents:")
    for name, role in agents.items():
        click.echo(f"  {name}: {role}")


@cli.command()
@click.argument("view_id")
def tableau_view(view_id: str):
    """Get details of a Tableau view using Bedrock."""
    asyncio.run(_tableau_view(view_id))


async def _chat(agent: str | None, workflow: bool, message: str):
    """Async chat handler."""
    try:
        system = LumosBedrockAgentSystem()
        messages = [Message(role="user", content=message)]

        result = await system.process_request(messages, agent=agent, workflow=workflow)

        if isinstance(result, Message):
            click.echo(result.content)
        else:
            click.echo(str(result))

    except Exception as e:
        logger.error(f"Error in chat: {e}")
        click.echo(f"Error: {str(e)}")


async def _tableau_view(view_id: str):
    """Async handler for getting Tableau view details."""
    try:
        system = LumosBedrockAgentSystem()
        messages = [
            Message(
                role="user", content=f"Get details for Tableau view with ID: {view_id}"
            )
        ]

        result = await system.process_request(messages, agent="tableau")
        if isinstance(result, Message):
            click.echo(result.content)
        else:
            click.echo(str(result))

    except Exception as e:
        logger.error(f"Error getting Tableau view: {e}")
        click.echo(f"Error: {str(e)}")


async def _interactive_chat():
    """Interactive chat session with Bedrock."""
    system = LumosBedrockAgentSystem()

    click.echo("🤖 Welcome to Lumos AI Interactive Chat with AWS Bedrock!")
    click.echo(
        "Available agents: data_analyst, data_manager, list_metrics, query_metrics, tableau"
    )
    click.echo("Type 'help' for commands, 'quit' or 'exit' to end the session.\\n")

    current_agent = None

    while True:
        try:
            # Get user input
            if current_agent:
                prompt = f"[{current_agent}] > "
            else:
                prompt = "lumos-bedrock > "

            user_input = click.prompt(prompt, type=str).strip()

            if not user_input:
                continue

            # Handle special commands
            if user_input.lower() in ["quit", "exit", "q"]:
                click.echo("👋 Goodbye!")
                break
            elif user_input.lower() == "help":
                _show_help()
                continue
            elif user_input.startswith("/agent "):
                agent_name = user_input[7:].strip()
                available_agents = system.list_agents()
                if agent_name in available_agents:
                    current_agent = agent_name
                    click.echo(f"✅ Switched to {agent_name} agent")
                else:
                    click.echo(f"❌ Unknown agent: {agent_name}")
                    click.echo(
                        "Available agents: " + ", ".join(available_agents.keys())
                    )
                continue
            elif user_input == "/reset":
                current_agent = None
                click.echo("✅ Reset to default agent")
                continue
            elif user_input == "/workflow":
                # Next message will use workflow mode
                user_input = click.prompt("Enter workflow message: ", type=str).strip()
                if user_input:
                    messages = [Message(role="user", content=user_input)]
                    result = await system.process_request(messages, workflow=True)
                    _display_result(result)
                continue

            # Process regular chat message
            messages = [Message(role="user", content=user_input)]
            result = await system.process_request(messages, agent=current_agent)
            _display_result(result)

        except KeyboardInterrupt:
            click.echo("\\n👋 Goodbye!")
            break
        except EOFError:
            click.echo("\\n👋 Goodbye!")
            break
        except Exception as e:
            logger.error(f"Error in interactive chat: {e}")
            click.echo(f"❌ Error: {str(e)}")


def _show_help():
    """Show help information for interactive chat."""
    click.echo("\\n📋 Interactive Chat Commands:")
    click.echo("  /agent <name>  - Switch to specific agent")
    click.echo("  /reset         - Reset to default agent")
    click.echo("  /workflow      - Use workflow mode for next message")
    click.echo("  help          - Show this help")
    click.echo("  quit/exit/q   - End chat session")
    click.echo("\\n💬 Just type your message to chat with the current agent!")
    click.echo()


def _display_result(result):
    """Display chat result."""
    if isinstance(result, Message):
        click.echo(f"🤖 {result.content}")
    else:
        click.echo(f"🤖 {str(result)}")
    click.echo()


def main():
    """Main entry point for Bedrock app."""
    cli()


if __name__ == "__main__":
    main()
