"""Main Lumos AI application entry point."""

import asyncio

import click

from meccaai.apps.lumos_agents import LumosAgentSystem
from meccaai.core.logging import get_logger
from meccaai.core.types import Message

logger = get_logger(__name__)


@click.group()
def cli():
    """Lumos AI Multi-Agent System."""
    pass


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


def main():
    """Main entry point."""
    cli()


if __name__ == "__main__":
    main()
