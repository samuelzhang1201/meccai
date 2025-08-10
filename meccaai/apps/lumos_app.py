"""Main Lumos AI application entry point."""

import asyncio

import click

from meccaai.apps.lumos_agents import LumosAgentSystem
from meccaai.core.logging import get_logger
from meccaai.core.types import Message

logger = get_logger(__name__)


@click.group(invoke_without_command=True)
@click.option("--chat", is_flag=True, help="Start interactive chat mode")
@click.pass_context
def cli(ctx, chat):
    """Lumos AI Multi-Agent System."""
    if chat:
        # Start interactive chat mode
        asyncio.run(_interactive_chat())
        ctx.exit()
    elif ctx.invoked_subcommand is None:
        # Show help if no command and no --chat flag
        click.echo(ctx.get_help())


@cli.command()
@click.option(
    "--agent", "-a", help="Specific agent to use (manager, tableau, dbt, reporting)"
)
@click.option("--workflow", "-w", is_flag=True, help="Use orchestrated workflow")
@click.argument("message")
def chat(agent: str | None, workflow: bool, message: str):
    """Chat with the Lumos AI system."""
    asyncio.run(_chat(agent, workflow, message))


@cli.command()
def list_agents():
    """List all available agents."""
    system = LumosAgentSystem()
    agents = system.list_agents()

    click.echo("Available Agents:")
    for name, role in agents.items():
        click.echo(f"  {name}: {role}")


@cli.command()
@click.argument("token_name", default="Agent")
def tableau_pats(token_name: str):
    """List Tableau Personal Access Tokens."""
    asyncio.run(_tableau_pats(token_name))


@cli.command()
@click.argument("view_id")
def tableau_view(view_id: str):
    """Get details of a Tableau view."""
    asyncio.run(_tableau_view(view_id))


@cli.command()
@click.argument("view_id")
@click.option("--filters", "-f", help="JSON string of filter parameters")
def tableau_pdf(view_id: str, filters: str | None):
    """Export a Tableau view as PDF."""
    import json

    filter_params = None
    if filters:
        try:
            filter_params = json.loads(filters)
        except json.JSONDecodeError:
            click.echo("Error: Invalid JSON in filters parameter")
            return

    asyncio.run(_tableau_pdf(view_id, filter_params))


async def _chat(agent: str | None, workflow: bool, message: str):
    """Async chat handler."""
    try:
        system = LumosAgentSystem()
        messages = [Message(role="user", content=message)]

        if workflow:
            results = await system.process_request(messages, workflow=True)
            if isinstance(results, list):
                for i, result in enumerate(results, 1):
                    click.echo(f"Agent {i} Response:")
                    click.echo(result.content)
                    click.echo("-" * 50)
            else:
                click.echo(results.content)
        else:
            result = await system.process_request(messages, agent=agent)
            if isinstance(result, Message):
                click.echo(result.content)
            else:
                for i, msg in enumerate(result, 1):
                    click.echo(f"Response {i}: {msg.content}")

    except Exception as e:
        logger.error(f"Error in chat: {e}")
        click.echo(f"Error: {str(e)}")


async def _tableau_pats(token_name: str):
    """Async handler for listing Tableau PATs."""
    try:
        system = LumosAgentSystem()
        messages = [
            Message(
                role="user",
                content="List all personal access tokens in our Tableau site",
            )
        ]

        result = await system.process_request(messages, agent="tableau")
        if isinstance(result, Message):
            click.echo(result.content)
        else:
            for msg in result:
                click.echo(msg.content)

    except Exception as e:
        logger.error(f"Error listing Tableau PATs: {e}")
        click.echo(f"Error: {str(e)}")


async def _tableau_view(view_id: str):
    """Async handler for getting Tableau view details."""
    try:
        system = LumosAgentSystem()
        messages = [
            Message(
                role="user", content=f"Get details for Tableau view with ID: {view_id}"
            )
        ]

        result = await system.process_request(messages, agent="tableau")
        if isinstance(result, Message):
            click.echo(result.content)
        else:
            for msg in result:
                click.echo(msg.content)

    except Exception as e:
        logger.error(f"Error getting Tableau view: {e}")
        click.echo(f"Error: {str(e)}")


async def _tableau_pdf(view_id: str, filter_params: dict | None):
    """Async handler for exporting Tableau view to PDF."""
    try:
        system = LumosAgentSystem()

        message_content = f"Export Tableau view {view_id} to PDF"
        if filter_params:
            message_content += f" with filters: {filter_params}"

        messages = [Message(role="user", content=message_content)]

        result = await system.process_request(messages, agent="tableau")
        if isinstance(result, Message):
            click.echo(result.content)
        else:
            for msg in result:
                click.echo(msg.content)

    except Exception as e:
        logger.error(f"Error exporting Tableau PDF: {e}")
        click.echo(f"Error: {str(e)}")


async def _interactive_chat():
    """Interactive chat session."""
    system = LumosAgentSystem()

    click.echo("🤖 Welcome to Lumos AI Interactive Chat!")
    click.echo("Available agents: manager, tableau, dbt, reporting, security")
    click.echo("Type 'help' for commands, 'quit' or 'exit' to end the session.\n")

    current_agent = None

    while True:
        try:
            # Get user input
            if current_agent:
                prompt = f"[{current_agent}] > "
            else:
                prompt = "lumos > "

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
                if agent_name in system.agents:
                    current_agent = agent_name
                    click.echo(f"✅ Switched to {agent_name} agent")
                else:
                    click.echo(f"❌ Unknown agent: {agent_name}")
                    click.echo("Available agents: " + ", ".join(system.agents.keys()))
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
            click.echo("\n👋 Goodbye!")
            break
        except EOFError:
            click.echo("\n👋 Goodbye!")
            break
        except Exception as e:
            logger.error(f"Error in interactive chat: {e}")
            click.echo(f"❌ Error: {str(e)}")


def _show_help():
    """Show help information for interactive chat."""
    click.echo("\n📋 Interactive Chat Commands:")
    click.echo(
        "  /agent <name>  - Switch to specific agent (manager, tableau, dbt, reporting, security)"
    )
    click.echo("  /reset         - Reset to default agent")
    click.echo("  /workflow      - Use workflow mode for next message")
    click.echo("  help          - Show this help")
    click.echo("  quit/exit/q   - End chat session")
    click.echo("\n💬 Just type your message to chat with the current agent!")
    click.echo()


def _display_result(result):
    """Display chat result."""
    if isinstance(result, Message):
        click.echo(f"🤖 {result.content}")
    elif isinstance(result, list):
        for i, msg in enumerate(result, 1):
            click.echo(f"🤖 Agent {i}: {msg.content}")
            if i < len(result):
                click.echo("-" * 50)
    click.echo()


def main():
    """Main entry point."""
    cli()


if __name__ == "__main__":
    main()
