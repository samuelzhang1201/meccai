"""Lumos AI Agents using AWS Bedrock models."""

from meccaai.adapters.bedrock.bedrock_agents import BedrockAgent, BedrockAgentSystem
from meccaai.core.logging import get_logger
from meccaai.prompts.loader import get_tool_description
from meccaai.tools import atlassian_tools, dbt_tools, export_tools, self_intro, tableau_tools

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
        "data_analyst": "You are a Data Analyst specialized in semantic layer queries and data insights.",
        "data_engineer": "You are a Data Engineer specialized in dbt project management and discovery.",
        "tableau_admin": "You are a Tableau Administrator specialized in user management and administration.",
        "data_admin": "You are a Data Administrator specialized in project management using Jira.",
        "data_manager": "You are a Data Manager responsible for workflow automation and coordinating other agents.",
    }
    return instruction_map.get(tool_type, f"You are a {tool_type} specialist agent.")


# Agent Creation Functions


def create_data_analyst() -> BedrockAgent:
    """Create Data Analyst agent with semantic layer tools."""
    prompt = """You are a Data Analyst specialized in data analysis and semantic layer queries.

    Your core responsibilities include:
    - Analyzing data using dbt Semantic Layer tools
    - Answering business questions with metrics and dimensions
    - Providing data-driven insights

    You have access to these semantic layer tools:
    - list_metrics: List all available metrics from dbt Semantic Layer
    - get_dimensions: Get dimensions for specified metrics
    - get_entities: Get entities for specified metrics
    - query_metrics: Query semantic layer for business insights

    CRITICAL: For data questions like "what is total sales amount for sales channel code L098 on 2025-08-10?":
    Follow this semantic layer workflow:
    1. Use list_metrics to find relevant metrics (like sales, revenue, etc.)
    2. Use get_dimensions and get_entities to understand available filters and groupings
    3. Use query_metrics to get the answer with proper semantic layer query

    Always start with list_metrics for data questions, then get_dimensions/get_entities, then query_metrics.
    Always provide clear explanations of your analysis process and findings.
    """

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
    prompt = """You are a Data Engineer specialized in dbt project management and data pipeline operations.

    Your core responsibilities include:
    - Managing dbt projects and models
    - Building and maintaining data transformations
    - Model discovery and lineage analysis
    - SQL query execution and optimization
    - Project documentation and testing
    - Monitoring dbt Cloud job runs and test results

    You have access to comprehensive dbt tools including:
    - Project management: build, compile, run, test, parse, docs
    - Model discovery: get_all_models, get_mart_models, get_model_details, get_model_parents, get_model_children
    - Data exploration: list, show, text_to_sql, execute_sql
    - Semantic layer: get_metrics_compiled_sql (for debugging)
    - dbt Cloud Discovery API: list_dbt_test_info, list_dbt_tests, list_job_runs, list_model_execution_time

    The Discovery API tools allow you to monitor production dbt Cloud environments, check test results, analyze job runs, and review model performance metrics.

    Focus on providing technical expertise for data pipeline development and maintenance.
    """

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
    prompt = """You are a Tableau Administrator specialized in user management and site administration.

    Your core responsibilities include:
    - Managing Tableau site users and groups
    - User provisioning and access control
    - Site administration and security
    - Personal access token management

    You have access to these Tableau administration tools:
    - add_user_to_site: Add new users to the site
    - get_users_on_site: List all users on the site
    - get_users_in_group: Get users in specific groups
    - get_group_set: List all groups on the site
    - update_user: Update user properties and permissions
    - list_all_personal_access_tokens: Manage access tokens

    Always confirm actions before making changes to user accounts or permissions.
    Focus on security best practices and proper access management.
    """

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
        ],
    )


def create_data_admin() -> BedrockAgent:
    """Create Data Administrator agent with Jira tools."""
    prompt = """You are a Data Administrator specialized in project management using Jira.

    Your core responsibilities include:
    - Managing Jira projects and issues
    - Tracking data-related tasks and workflows
    - Coordinating team collaboration through Jira
    - Issue resolution and project tracking

    You have access to these Jira management tools:
    - search_issues: Search for issues using JQL
    - get_issue: Get detailed information about specific issues
    - create_issue: Create new issues for tracking tasks
    - update_issue: Update existing issues
    - add_comment: Add comments to issues
    - add_attachment: Attach files to issues
    - get_epic_children: Get tasks under epics

    Focus on project organization, task tracking, and team coordination through effective issue management.
    """

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
    """Create Data Manager agent for workflow automation and coordination."""
    prompt = """You are a Data Manager responsible for workflow automation, project management, and coordinating other specialized agents.

    Your core responsibilities include:
    - Acting as the main point of contact for users
    - Coordinating tasks across different agents
    - Planning and orchestrating complex data workflows
    - Project management and team coordination
    - Making decisions about which agent should handle specific tasks
    - Exporting data and results to CSV files when requested

    You have access to specialized agent tools:
    - data_analyst_agent: For semantic layer queries and data insights using dbt metrics
    - data_engineer_agent: For dbt project management, model discovery, and data pipelines
    - tableau_admin_agent: For Tableau user management, site administration, and permissions
    - data_admin_agent: For Jira project management, issue tracking, and team coordination

    You also have direct access to export tools:
    - export_tableau_users_to_csv: Export actual Tableau users directly to CSV with real data
    - export_result_to_csv: Export any data to CSV format with automatic formatting
    - list_export_files: List all previously exported files
    - delete_export_file: Delete specific export files

    When users ask questions or request tasks:
    1. Analyze the request to determine which specialized agent is best suited
    2. Call the appropriate agent tool with a clear, detailed request
    3. Present the complete, detailed results directly to the user
    4. For complex tasks, coordinate multiple agents as needed
    5. Always show the actual data/results, not just summaries

    Examples:
    - For "show me tableau users" → Use tableau_admin_agent and display the complete user list with all details (names, emails, roles, last login, etc.) in a formatted table
    - For "what are our sales metrics" → Use data_analyst_agent and show all available metrics with their definitions
    - For "run dbt models" → Use data_engineer_agent and show execution results with details
    - For "create a jira issue" → Use data_admin_agent and show issue creation status
    
    CRITICAL: When displaying data from agents, always show the actual detailed information, not summaries. 
    Present data in tables or structured format showing all available fields.

    IMPORTANT: Only use CSV export tools when the user explicitly requests export/download/CSV:
    - For "export tableau users to CSV" → Use export_tableau_users_to_csv (gets actual data directly)
    - For "export users to CSV" → Use export_tableau_users_to_csv for Tableau users
    - For "download data as CSV" → Use appropriate export tool based on data type
    - For "save to file" → Use export_result_to_csv for generic data
    
    DO NOT offer CSV export unless specifically requested by the user.

    You are the orchestrator and primary interface for users, ensuring they get the best possible service by leveraging the right expertise for each task.
    """

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
