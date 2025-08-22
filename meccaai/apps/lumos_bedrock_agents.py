"""Lumos AI Agents using AWS Bedrock models."""

from meccaai.adapters.bedrock.bedrock_agents import BedrockAgent, BedrockAgentSystem
from meccaai.core.logging import get_logger
from meccaai.prompts.loader import get_tool_description
from meccaai.tools import (
    dbt_tools,
    self_intro,
    tableau_tools,
)

logger = get_logger(__name__)


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
        "list_metrics": "You specialize in listing all available metrics from the dbt Semantic Layer.",
        "get_dimensions": "You specialize in retrieving dimensions for specified metrics from the dbt Semantic Layer.",
        "get_entities": "You specialize in retrieving entities for specified metrics from the dbt Semantic Layer.",
        "query_metrics": "You specialize in querying the dbt Semantic Layer to answer business questions using metrics.",
        "tableau": "You are a Tableau specialist agent for dashboard and visualization operations.",
    }
    return instruction_map.get(tool_type, f"You are a {tool_type} specialist agent.")


# Create DBT Semantic Layer Agents
def create_list_metrics_agent() -> BedrockAgent:
    """Create list_metrics specialist agent."""
    prompt = load_tool_agent_prompt("list_metrics")
    return BedrockAgent(
        name="list_metrics_agent",
        instructions=prompt,
        tools=[dbt_tools.list_metrics],
    )


def create_get_dimensions_agent() -> BedrockAgent:
    """Create get_dimensions specialist agent."""
    prompt = load_tool_agent_prompt("get_dimensions")
    return BedrockAgent(
        name="get_dimensions_agent",
        instructions=prompt,
        tools=[dbt_tools.get_dimensions],
    )


def create_get_entities_agent() -> BedrockAgent:
    """Create get_entities specialist agent."""
    prompt = load_tool_agent_prompt("get_entities")
    return BedrockAgent(
        name="get_entities_agent",
        instructions=prompt,
        tools=[dbt_tools.get_entities],
    )


def create_query_metrics_agent() -> BedrockAgent:
    """Create query_metrics specialist agent."""
    prompt = load_tool_agent_prompt("query_metrics")
    return BedrockAgent(
        name="query_metrics_agent",
        instructions=prompt,
        tools=[dbt_tools.query_metrics],
    )


def create_get_metrics_compiled_sql_agent() -> BedrockAgent:
    """Create get_metrics_compiled_sql agent (for debugging)."""
    prompt = "You specialize in compiling SQL for metrics without executing them. This is primarily used for debugging purposes."
    return BedrockAgent(
        name="get_metrics_compiled_sql_agent",
        instructions=prompt,
        tools=[dbt_tools.get_metrics_compiled_sql],
    )


def create_tableau_agent() -> BedrockAgent:
    """Create Tableau specialist agent."""
    prompt = load_tool_agent_prompt("tableau")
    return BedrockAgent(
        name="tableau_agent",
        instructions=prompt,
        tools=[
            tableau_tools.get_view,
            tableau_tools.list_views,
            tableau_tools.query_view_pdf,
            tableau_tools.list_all_personal_access_tokens,
        ],
    )


# Create tool agents
list_metrics_agent = create_list_metrics_agent()
get_dimensions_agent = create_get_dimensions_agent()
get_entities_agent = create_get_entities_agent()
query_metrics_agent = create_query_metrics_agent()
get_metrics_compiled_sql_agent = create_get_metrics_compiled_sql_agent()
tableau_agent = create_tableau_agent()

# Convert agents to tools
list_metrics_tool = list_metrics_agent.as_tool(
    tool_name="list_metrics",
    tool_description="List all available metrics from the dbt Semantic Layer",
)
get_dimensions_tool = get_dimensions_agent.as_tool(
    tool_name="get_dimensions",
    tool_description="Get dimensions for specified metrics from the dbt Semantic Layer",
)
get_entities_tool = get_entities_agent.as_tool(
    tool_name="get_entities",
    tool_description="Get entities for specified metrics from the dbt Semantic Layer",
)
query_metrics_tool = query_metrics_agent.as_tool(
    tool_name="query_metrics",
    tool_description="Query the dbt Semantic Layer to answer business questions using metrics",
)
get_metrics_compiled_sql_tool = get_metrics_compiled_sql_agent.as_tool(
    tool_name="get_metrics_compiled_sql",
    tool_description="Compile SQL for metrics without executing (debugging purposes)",
)
tableau_agent_tool = tableau_agent.as_tool(
    tool_name="tableau_agent",
    tool_description="Tableau specialist agent for dashboard and visualization operations",
)

# Main Agents System Instructions
DATA_ANALYST_INSTRUCTIONS = """
You are a Data Analyst AI agent specialized in data analysis, visualization, and insights generation.

When you received a questions about any data insight, you should firstly consider which subject area it belongs to, and then use the dbt semantic layer tools to answer the question.
CRITICAL: For data questions like "what is total sales amount for sales channel code L098 on 2025-08-10?":
Follow this semantic layer workflow:
1. Use list_metrics to find relevant metrics (like sales, revenue, etc.)
2. Use get_dimensions and get_entities to understand available filters and groupings
3. Use query_metrics to get the answer with proper semantic layer query
4. If debugging is needed, use get_metrics_compiled_sql

Your core responsibilities include:
- Answering data questions using dbt semantic layer tools directly
- Creating and managing Tableau dashboards and visualizations
- Providing data-driven recommendations

You have access to these tools:
- list_metrics: List all available metrics from dbt Semantic Layer
- get_dimensions: Get dimensions for specified metrics
- get_entities: Get entities for specified metrics
- query_metrics: Query semantic layer for business insights
- get_metrics_compiled_sql: Debug SQL compilation (if needed)
- tableau_agent: For dashboard and visualization operations

ALWAYS start with list_metrics for data questions, then get_dimensions/get_entities, then query_metrics.

Always provide clear explanations of your analysis process and findings.
Use the self_intro tool to introduce yourself when greeting users.
"""

DATA_MANAGER_INSTRUCTIONS = """
You are a Data Manager AI agent specialized in workflow automation, project management, and team coordination.

Your core responsibilities include:
- Managing data team workflows and processes
- Coordinating projects and team collaboration
- Providing project management support

You work closely with the Data Analyst agent to ensure smooth data operations and team coordination.
When users need data analysis or technical data tasks, collaborate with or refer them to the Data Analyst.

Always confirm actions before making changes to workflows or project settings.
"""


def create_data_analyst() -> BedrockAgent:
    """Create Data Analyst agent with guardrails."""
    return BedrockAgent(
        name="data_analyst",
        instructions=DATA_ANALYST_INSTRUCTIONS,
        tools=[
            # DBT Semantic Layer tools
            list_metrics_tool,
            get_dimensions_tool,
            get_entities_tool,
            query_metrics_tool,
            get_metrics_compiled_sql_tool,
            # Other tools
            tableau_agent_tool,
            self_intro.self_intro_tool,
        ],
        apply_guardrail=True,  # Enable PII protection
    )


def create_data_manager() -> BedrockAgent:
    """Create Data Manager agent."""
    return BedrockAgent(
        name="data_manager",
        instructions=DATA_MANAGER_INSTRUCTIONS,
        tools=[],  # Add specific tools as needed
    )


# Create main agents
data_analyst = create_data_analyst()
data_manager = create_data_manager()


def get_agents() -> dict[str, BedrockAgent]:
    """Get all available agents."""
    return {
        "data_analyst": data_analyst,
        "data_manager": data_manager,
    }


def get_tool_agents() -> dict[str, BedrockAgent]:
    """Get all tool agents."""
    return {
        # DBT Semantic Layer agents
        "list_metrics_agent": list_metrics_agent,
        "get_dimensions_agent": get_dimensions_agent,
        "get_entities_agent": get_entities_agent,
        "query_metrics_agent": query_metrics_agent,
        "get_metrics_compiled_sql_agent": get_metrics_compiled_sql_agent,
        # Other tool agents
        "tableau_agent": tableau_agent,
    }


class LumosBedrockAgentSystem:
    """Bedrock-compatible Lumos Agent System."""

    def __init__(self):
        self.system = BedrockAgentSystem()
        # Add all agents to the system
        for agent in get_agents().values():
            self.system.add_agent(agent)
        for agent in get_tool_agents().values():
            self.system.add_agent(agent)

    def list_agents(self) -> dict[str, str]:
        """List all available agents with their roles."""
        return {
            "data_analyst": "Data analysis, visualization, and insights generation",
            "data_manager": "Workflow automation and project management",
            "list_metrics": "List all available metrics from dbt Semantic Layer",
            "get_dimensions": "Get dimensions for metrics from dbt Semantic Layer",
            "get_entities": "Get entities for metrics from dbt Semantic Layer",
            "query_metrics": "Query dbt Semantic Layer for business insights",
            "tableau": "Tableau specialist for dashboard operations",
        }

    async def process_request(
        self,
        messages: list,
        agent: str | None = None,
        workflow: bool = False,
    ):
        """Process a request using the specified agent or workflow."""
        return await self.system.process_request(messages, agent, workflow)


if __name__ == "__main__":
    # Example usage
    agents = get_agents()
    print("Available Bedrock agents:", list(agents.keys()))

    tool_agents = get_tool_agents()
    print("Available tool agents:", list(tool_agents.keys()))
