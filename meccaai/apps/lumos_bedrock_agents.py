"""Lumos AI Agents using AWS Bedrock models."""

from meccaai.adapters.bedrock.bedrock_agents import BedrockAgent, BedrockAgentSystem
from meccaai.core.logging import get_logger
from meccaai.prompts.loader import get_tool_description
from meccaai.tools import (
    atlassian_tools,
    dbt_tools,
    export_tools,
    self_intro,
    tableau_tools,
)

logger = get_logger(__name__)


def load_agent_prompt(agent_name: str) -> str:
    """Load agent prompt from agents directory."""
    try:
        # Load agent prompt from agents directory
        prompt = get_tool_description(f"agents/{agent_name}.md")
        if prompt:
            return prompt
    except Exception as e:
        logger.warning(f"Could not load agent prompt for {agent_name}: {e}")

    # Fallback to default instructions
    instruction_map = {
        "data_analyst": "You are a Data Analyst specialized in semantic layer queries and data insights.",
        "data_engineer": "You are a Data Engineer specialized in dbt project management and discovery.",
        "tableau_admin": "You are a Tableau Administrator specialized in user management and administration.",
        "data_admin": "You are a Data Administrator specialized in project management using Jira.",
        "data_manager": "You are a Data Manager responsible for workflow automation and coordinating other agents, and final reporting",
    }
    return instruction_map.get(agent_name, f"You are a {agent_name} specialist agent.")


def load_tool_agent_prompt(tool_type: str) -> str:
    """Load tool agent prompt from description files."""
    try:
        # Try to get tool description from prompts directory
        description = get_tool_description(f"semantic_layer/{tool_type}.md")
        if description:
            return description
    except Exception:
        # Try general prompt
        try:
            description = get_tool_description(f"{tool_type}.md")
            if description:
                return description
        except Exception as e:
            logger.warning(f"Could not load tool description for {tool_type}: {e}")

    # Fallback to default instructions
    instruction_map = {
        "data_analyst": "You are a Data Analyst specialized in semantic layer queries and data insights.",
        "data_engineer": "You are a Data Engineer specialized in dbt project management and discovery.",
        "tableau_admin": "You are a Tableau Administrator specialized in user management and administration.",
        "data_admin": "You are a Data Administrator specialized in project management using Jira.",
        "data_manager": "You are a Data Manager responsible for workflow automation and coordinating other agents, and final reporting",
    }
    return instruction_map.get(tool_type, f"You are a {tool_type} specialist agent.")


# Agent Creation Functions


def create_data_analyst() -> BedrockAgent:
    """Create Data Analyst agent with semantic layer tools."""
    prompt = load_agent_prompt("data_analyst")

    return BedrockAgent(
        name="data_analyst",
        instructions=prompt,
        tools=[
            dbt_tools.list_metrics,
            dbt_tools.get_dimensions,
            dbt_tools.get_entities,
            dbt_tools.query_metrics,
            self_intro.self_intro_tool,
        ],
        apply_guardrail=True,  # Enable PII protection
    )


def create_data_engineer() -> BedrockAgent:
    """Create Data Engineer agent with all dbt discovery tools."""
    prompt = load_agent_prompt("data_engineer")

    return BedrockAgent(
        name="data_engineer",
        instructions=prompt,
        tools=[
            # dbt CLI Tools
            dbt_tools.build,
            dbt_tools.compile,
            dbt_tools.run,
            dbt_tools.test,
            dbt_tools.parse,
            dbt_tools.docs,
            dbt_tools.list_resources,
            dbt_tools.show,
            # Discovery Tools
            dbt_tools.get_all_models,
            dbt_tools.get_mart_models,
            dbt_tools.get_model_details,
            dbt_tools.get_model_parents,
            dbt_tools.get_model_children,
            # SQL Tools
            dbt_tools.text_to_sql,
            dbt_tools.execute_sql,
            dbt_tools.get_metrics_compiled_sql,
            # dbt Cloud Discovery API Tools
            dbt_tools.list_dbt_test_info,
            dbt_tools.list_dbt_tests,
            dbt_tools.list_job_runs,
            dbt_tools.list_model_execution_time,
        ],
    )


def create_tableau_admin() -> BedrockAgent:
    """Create Tableau Administrator agent with user management tools."""
    prompt = load_agent_prompt("tableau_admin")

    return BedrockAgent(
        name="tableau_admin",
        instructions=prompt,
        tools=[
            tableau_tools.add_user_to_site,
            tableau_tools.get_users_on_site,
            tableau_tools.get_users_in_group,
            tableau_tools.get_group_set,
            tableau_tools.update_user,
            tableau_tools.list_all_personal_access_tokens,
            tableau_tools.get_content_usage,
            tableau_tools.get_datasources,
            tableau_tools.get_workbooks,
            tableau_tools.get_views_on_site,
        ],
    )


def create_data_admin() -> BedrockAgent:
    """Create Data Administrator agent with Jira tools."""
    prompt = load_agent_prompt("data_admin")

    return BedrockAgent(
        name="data_admin",
        instructions=prompt,
        tools=[
            atlassian_tools.search_issues,
            atlassian_tools.get_issue,
            atlassian_tools.create_issue,
            atlassian_tools.update_issue,
            atlassian_tools.add_comment,
            atlassian_tools.add_attachment,
            atlassian_tools.get_epic_children,
        ],
    )



def create_data_manager() -> BedrockAgent:
    """Create Data Manager agent for workflow automation, coordination, reporting, and analysis."""
    prompt = load_agent_prompt("data_manager")

    # Note: We'll add the agent tools after all agents are created
    return BedrockAgent(
        name="data_manager",
        instructions=prompt,
        tools=[
            self_intro.self_intro_tool,
            export_tools.export_tableau_users_to_csv,
            export_tools.export_result_to_csv,
            export_tools.list_export_files,
            export_tools.delete_export_file,
        ],
    )


# Create main agents
data_analyst = create_data_analyst()
data_engineer = create_data_engineer()
tableau_admin = create_tableau_admin()
data_admin = create_data_admin()
data_manager = create_data_manager()

# Add other agents as tools to the data_manager
data_manager.tools.extend(
    [
        data_analyst.as_tool(
            tool_name="data_analyst_agent",
            tool_description="Data Analyst agent for semantic layer queries, metrics analysis, and data insights using dbt Semantic Layer tools.",
        ),
        data_engineer.as_tool(
            tool_name="data_engineer_agent",
            tool_description="Data Engineer agent for dbt project management, model discovery, SQL execution, and data pipeline operations.",
        ),
        tableau_admin.as_tool(
            tool_name="tableau_admin_agent",
            tool_description="Tableau Administrator agent for user management, site administration, group management, and access control.",
        ),
        data_admin.as_tool(
            tool_name="data_admin_agent",
            tool_description="Data Administrator agent for Jira project management, issue tracking, task coordination, and team collaboration.",
        ),
    ]
)


def get_agents() -> dict[str, BedrockAgent]:
    """Get all main agents."""
    return {
        "data_analyst": data_analyst,
        "data_engineer": data_engineer,
        "tableau_admin": tableau_admin,
        "data_admin": data_admin,
        "data_manager": data_manager,
    }


class LumosBedrockAgentSystem:
    """Bedrock-compatible Lumos Agent System."""

    def __init__(self):
        self.system = BedrockAgentSystem()
        # Add all agents to the system
        for agent in get_agents().values():
            self.system.add_agent(agent)

    def list_agents(self) -> dict[str, str]:
        """List all available agents with their roles."""
        return {
            "data_analyst": "Data analysis and semantic layer queries specialist",
            "data_engineer": "dbt project management and data pipeline specialist",
            "tableau_admin": "Tableau user management and administration specialist",
            "data_admin": "Jira project management and issue tracking specialist",
            "data_manager": "Workflow automation and team coordination lead",
        }

    async def process_request(
        self,
        messages: list,
        agent: str | None = None,
        workflow: bool = False,
    ):
        """Process a request using the specified agent or workflow."""
        # Default to data_manager if no agent specified - they will coordinate
        target_agent = (
            agent if agent and agent in self.system.agents else "data_manager"
        )

        return await self.system.process_request(
            messages, agent=target_agent, workflow=workflow
        )


if __name__ == "__main__":
    # Example usage
    agents = get_agents()
    print("Available Bedrock agents:", list(agents.keys()))

    system = LumosBedrockAgentSystem()
    print("Agent roles:", system.list_agents())
