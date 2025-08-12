"""Lumos AI Agents using OpenAI Agent SDK Framework."""


from agents import Agent, OutputGuardrail, handoff, FunctionTool, GuardrailFunctionOutput, set_default_openai_key

from meccaai.core.config import settings
from meccaai.core.logging import get_logger
from meccaai.prompts.loader import get_tool_description
from meccaai.tools import (
    atlassian_tools,
    cortex_agent_tools,
    dbt_tools,
    self_intro,
    tableau_tools,
)
import json

logger = get_logger(__name__)

# Set the default OpenAI API key for the agents
if settings.openai_api_key:
    set_default_openai_key(settings.openai_api_key)

# PII leak indicators for output guardrail
LEAK_INDICATORS = ["password", "secret", "confidential", "private"]


def check_pii_leak(content: str) -> bool:
    """Check if content contains PII leak indicators.

    Args:
        content: Content to check

    Returns:
        True if PII leak detected, False otherwise
    """
    content_lower = content.lower()
    return any(indicator in content_lower for indicator in LEAK_INDICATORS)


def output_guardrail(content: str) -> str:
    """Apply output guardrail to check for PII leaks.

    Args:
        content: Content to check and potentially redact

    Returns:
        Original content or redacted message
    """
    if check_pii_leak(content):
        logger.warning("PII leak detected in output, content redacted")
        return "Content has been redacted due to potential PII information."
    return content


# Adapter: convert internal BaseTool/MCPTool to OpenAI Agent SDK FunctionTool
def to_function_tool(internal_tool):
    async def on_invoke(context, tool_input: str | None):
        kwargs = json.loads(tool_input) if tool_input else {}
        result = await internal_tool.call(**kwargs)
        return result.result if hasattr(result, "result") else str(result)

    return FunctionTool(
        name=internal_tool.name,
        description=internal_tool.description,
        params_json_schema=internal_tool.parameters,
        on_invoke_tool=on_invoke,
    )


# Tool Agent System Instructions
DBT_AGENT_INSTRUCTIONS = """
You are a dbt (data build tool) specialist agent. You help users with data insights using the semantic layer.

CRITICAL: When users ask data questions like "what is total sales amount for sales channel code L098 on 2025-08-10?":

1. FIRST: Use list_metrics to find relevant metrics (like sales, revenue, etc.)
2. THEN: Use get_dimensions and get_entities to understand available filters
3. FINALLY: Use query_metrics with proper semantic layer syntax

DO NOT convert questions to SQL - always use the semantic layer tools in this order:
list_metrics -> get_dimensions -> get_entities -> query_metrics

For other tasks:
- Building and running dbt models
- Testing data models  
- Managing dbt documentation
- Model lineage and discovery

Always use the semantic layer approach for data questions first.
"""

TABLEAU_AGENT_INSTRUCTIONS = """
You are a Tableau specialist agent. You help users with:
- Creating and managing Tableau workbooks and dashboards
- Publishing content to Tableau Server/Cloud
- Extracting data from Tableau
- Managing Tableau permissions and users
- Troubleshooting Tableau connectivity issues

Use the provided Tableau tools to interact with Tableau Server/Cloud.
Always verify permissions and provide clear explanations of actions taken.
"""

SNOWFLAKE_AGENT_INSTRUCTIONS = """
You are a Snowflake specialist agent using Cortex AI capabilities. You help users with:
- only if dbt semantic layer query is not enough, you can use snowflake cortex ai to answer the question.
- Executing SQL queries in Snowflake
- Data analysis and insights
- Performance optimization
- Data warehouse management

Use the provided Cortex agent tools for Snowflake interactions.
Always validate queries and explain results clearly.
"""

ZAPIER_AGENT_INSTRUCTIONS = """
You are a Zapier automation specialist agent. You help users with:
- Creating and managing Zapier workflows (Zaps)
- Connecting different applications
- Automating business processes
- Troubleshooting automation issues
- Optimizing workflow efficiency

Use the provided Zapier tools to manage automations.
Always confirm actions before making changes to live workflows.
"""

ATLASSIAN_AGENT_INSTRUCTIONS = """
You are an Atlassian suite specialist agent. You help users with:
- Managing Jira projects, issues, and workflows
- Creating and updating Confluence pages
- Coordinating team collaboration
- Project management and tracking
- Knowledge management

Use the provided Atlassian tools for Jira and Confluence operations.
Always verify permissions and provide clear status updates.
"""


def load_tool_agent_prompt(tool_type: str) -> str:
    """Load tool agent prompt from description files.

    Args:
        tool_type: Type of tool (dbt, tableau, etc.)

    Returns:
        Loaded prompt content
    """
    try:
        # Try to get tool description from prompts directory
        description = get_tool_description(f"{tool_type}.md")
        if description:
            return description
    except Exception as e:
        logger.warning(f"Could not load tool description for {tool_type}: {e}")

    # Fallback to default instructions
    instruction_map = {
        "dbt": DBT_AGENT_INSTRUCTIONS,
        "tableau": TABLEAU_AGENT_INSTRUCTIONS,
        "snowflake": SNOWFLAKE_AGENT_INSTRUCTIONS,
        "zapier": ZAPIER_AGENT_INSTRUCTIONS,
        "atlassian": ATLASSIAN_AGENT_INSTRUCTIONS,
    }
    return instruction_map.get(tool_type, f"You are a {tool_type} specialist agent.")


# Create DBT Semantic Layer Tool Agents
def create_list_metrics_agent() -> Agent:
    """Create list_metrics specialist agent."""
    try:
        prompt = get_tool_description("semantic_layer/list_metrics.md")
    except Exception:
        prompt = "You specialize in listing all available metrics from the dbt Semantic Layer."
    
    return Agent(
        name="list_metrics_agent",
        model="gpt-4o-mini", 
        instructions=prompt,
        tools=[to_function_tool(dbt_tools.list_metrics)],
    )


def create_get_dimensions_agent() -> Agent:
    """Create get_dimensions specialist agent."""
    try:
        prompt = get_tool_description("semantic_layer/get_dimensions.md")
    except Exception:
        prompt = "You specialize in retrieving dimensions for specified metrics from the dbt Semantic Layer."
    
    return Agent(
        name="get_dimensions_agent",
        model="gpt-4o-mini",
        instructions=prompt,
        tools=[to_function_tool(dbt_tools.get_dimensions)],
    )


def create_get_entities_agent() -> Agent:
    """Create get_entities specialist agent."""
    try:
        prompt = get_tool_description("semantic_layer/get_entities.md")
    except Exception:
        prompt = "You specialize in retrieving entities for specified metrics from the dbt Semantic Layer."
    
    return Agent(
        name="get_entities_agent", 
        model="gpt-4o-mini",
        instructions=prompt,
        tools=[to_function_tool(dbt_tools.get_entities)],
    )


def create_query_metrics_agent() -> Agent:
    """Create query_metrics specialist agent."""
    try:
        prompt = get_tool_description("semantic_layer/query_metrics.md")
    except Exception:
        prompt = "You specialize in querying the dbt Semantic Layer to answer business questions using metrics."
    
    return Agent(
        name="query_metrics_agent",
        model="gpt-4o-mini", 
        instructions=prompt,
        tools=[to_function_tool(dbt_tools.query_metrics)],
    )


def create_get_metrics_compiled_sql_agent() -> Agent:
    """Create get_metrics_compiled_sql agent (for debugging)."""
    prompt = "You specialize in compiling SQL for metrics without executing them. This is primarily used for debugging purposes."
    
    return Agent(
        name="get_metrics_compiled_sql_agent",
        model="gpt-4o-mini",
        instructions=prompt,
        tools=[to_function_tool(dbt_tools.get_metrics_compiled_sql)],
    )


def create_tableau_agent() -> Agent:
    """Create Tableau specialist agent."""
    prompt = load_tool_agent_prompt("tableau")

    return Agent(
        name="tableau_agent",
        model="gpt-4o-mini",
        instructions=prompt,
        tools=[
            to_function_tool(tableau_tools.get_view),
            to_function_tool(tableau_tools.list_views),
            to_function_tool(tableau_tools.query_view_pdf),
            to_function_tool(tableau_tools.list_all_personal_access_tokens),
        ],
    )


def create_snowflake_agent() -> Agent:
    """Create Snowflake/Cortex specialist agent."""
    prompt = load_tool_agent_prompt("snowflake")

    return Agent(
        name="snowflake_agent",
        model="gpt-4o-mini",
        instructions=prompt,
        tools=[
            to_function_tool(cortex_agent_tools.run_cortex_agents),
        ],
    )


def create_zapier_agent() -> Agent:
    """Create Zapier specialist agent."""
    prompt = load_tool_agent_prompt("zapier")

    return Agent(
        name="zapier_agent",
        model="gpt-4o-mini",
        instructions=prompt,
        tools=[
            # Zapier tools are empty in this implementation
        ],
    )


def create_atlassian_agent() -> Agent:
    """Create Atlassian specialist agent."""
    prompt = load_tool_agent_prompt("atlassian")

    return Agent(
        name="atlassian_agent",
        model="gpt-4o-mini",
        instructions=prompt,
        tools=[
            to_function_tool(atlassian_tools.create_issue),
            to_function_tool(atlassian_tools.update_issue),
            to_function_tool(atlassian_tools.get_issue),
            to_function_tool(atlassian_tools.search_issues),
            to_function_tool(atlassian_tools.add_comment),
            to_function_tool(atlassian_tools.add_attachment),
            to_function_tool(atlassian_tools.get_epic_children),
        ],
    )


# Create DBT semantic layer tool agents
list_metrics_agent = create_list_metrics_agent()
get_dimensions_agent = create_get_dimensions_agent()
get_entities_agent = create_get_entities_agent()
query_metrics_agent = create_query_metrics_agent()
get_metrics_compiled_sql_agent = create_get_metrics_compiled_sql_agent()

# Create other tool agents
tableau_agent = create_tableau_agent()
snowflake_agent = create_snowflake_agent()
zapier_agent = create_zapier_agent()
atlassian_agent = create_atlassian_agent()

# Convert DBT semantic layer agents to tools using as_tool method
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

# Convert other agents to tools
tableau_agent_tool = tableau_agent.as_tool(
    tool_name="tableau_agent",
    tool_description="Tableau specialist agent for dashboard and visualization operations",
)
snowflake_agent_tool = snowflake_agent.as_tool(
    tool_name="snowflake_agent",
    tool_description="Snowflake/Cortex specialist agent for data warehouse operations",
)
zapier_agent_tool = zapier_agent.as_tool(
    tool_name="zapier_agent",
    tool_description="Zapier specialist agent for workflow automation",
)
atlassian_agent_tool = atlassian_agent.as_tool(
    tool_name="atlassian_agent",
    tool_description="Atlassian specialist agent for Jira and Confluence operations",
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
- snowflake_agent: For advanced Snowflake/Cortex operations

ALWAYS start with list_metrics for data questions, then get_dimensions/get_entities, then query_metrics.
For workflow orchestration or project management, hand off to the Data Manager agent.

Always provide clear explanations of your analysis process and findings.
Use the self_intro tool to introduce yourself when greeting users.
"""

DATA_MANAGER_INSTRUCTIONS = """
You are a Data Manager AI agent specialized in workflow automation, project management, and team coordination.

Your core responsibilities include:
- Managing data team workflows and processes
- Automating business processes using Zapier
- Coordinating projects through Jira and Confluence
- Managing team communication and documentation
- Orchestrating data pipeline operations

You have access to specialized agent tools for:
- Zapier operations (creating automations, managing workflows)
- Atlassian operations (Jira project management, Confluence documentation)

You work closely with the Data Analyst agent to ensure smooth data operations and team coordination.
When users need data analysis or technical data tasks, collaborate with or refer them to the Data Analyst.

Always confirm actions before making changes to workflows or project settings.
"""


def create_data_manager() -> Agent:
    """Create Data Manager agent."""
    return Agent(
        name="data_manager",
        model="gpt-4o-mini",
        instructions=DATA_MANAGER_INSTRUCTIONS,
        tools=[
            zapier_agent_tool,
            atlassian_agent_tool,
        ],
    )


# Create main agents (without handoffs first)
def create_agents():
    """Create and configure all agents with proper handoffs."""

    # Create data manager first
    data_manager = create_data_manager()

    # Create handoff from Data Analyst to Data Manager
    data_manager_handoff = handoff(
        data_manager,
        tool_name_override="request_data_manager_help",
        tool_description_override="Hand off to Data Manager for workflow automation, project management, and team coordination tasks",
    )

    # Create data analyst with handoff
    data_analyst = create_data_analyst_with_handoffs([data_manager_handoff])

    return data_analyst, data_manager


def create_data_analyst_with_handoffs(handoffs_list):
    """Create Data Analyst agent with specified handoffs."""

    # Create PII output guardrail
    def pii_guardrail_function(context, agent, agent_output):
        """PII guardrail function for output filtering (SDK signature)."""
        text = str(agent_output) if agent_output is not None else ""
        if check_pii_leak(text):
            return GuardrailFunctionOutput(
                output_info={"leakage_detected": True},
                tripwire_triggered=True,
            )
        return GuardrailFunctionOutput(
            output_info={"quality_check": "passed"},
            tripwire_triggered=False,
        )

    pii_guardrail = OutputGuardrail(pii_guardrail_function)

    agent = Agent(
        name="data_analyst",
        model="gpt-4o-mini",
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
            snowflake_agent_tool,
            to_function_tool(self_intro.self_intro_tool),
        ],
        handoffs=handoffs_list,
        output_guardrails=[pii_guardrail],
    )

    return agent


# Create agents
data_analyst, data_manager = create_agents()


# Handoff functionality
def handoff_to_data_manager(reason: str = "Task requires workflow management"):
    """Hand off from Data Analyst to Data Manager.

    Args:
        reason: Reason for handoff

    Returns:
        Handoff message
    """
    logger.info(f"Handoff from Data Analyst to Data Manager: {reason}")
    return f"Handing off to Data Manager. Reason: {reason}"


def get_agents() -> dict[str, Agent]:
    """Get all available agents.

    Returns:
        Dictionary of agent names to Agent objects
    """
    return {
        "data_analyst": data_analyst,
        "data_manager": data_manager,
    }


def get_tool_agents() -> dict[str, Agent]:
    """Get all tool agents.

    Returns:
        Dictionary of tool agent names to Agent objects
    """
    return {
        # DBT Semantic Layer agents
        "list_metrics_agent": list_metrics_agent,
        "get_dimensions_agent": get_dimensions_agent,
        "get_entities_agent": get_entities_agent,
        "query_metrics_agent": query_metrics_agent,
        "get_metrics_compiled_sql_agent": get_metrics_compiled_sql_agent,
        # Other tool agents
        "tableau_agent": tableau_agent,
        "snowflake_agent": snowflake_agent,
        "zapier_agent": zapier_agent,
        "atlassian_agent": atlassian_agent,
    }


class LumosAgentSystem:
    """Compatibility layer for the original Lumos Agent System interface."""
    
    def __init__(self):
        self.agents = get_agents()
        self.tool_agents = get_tool_agents()
    
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
            "snowflake": "Snowflake/Cortex specialist for data warehouse operations",
        }
    
    async def process_request(
        self, 
        messages: list, 
        agent: str | None = None, 
        workflow: bool = False
    ):
        """Process a request using the specified agent or workflow."""
        from meccaai.core.types import Message
        from agents import Runner
        
        # Extract the user message
        user_message = messages[-1].content if messages else ""
        
        if workflow:
            # Use Data Analyst with potential handoff to Data Manager
            selected_agent = self.agents["data_analyst"]
        elif agent:
            # Map agent names to actual agents
            agent_mapping = {
                "data_analyst": self.agents["data_analyst"],
                "data_manager": self.agents["data_manager"],
                "list_metrics": self.tool_agents["list_metrics_agent"],
                "get_dimensions": self.tool_agents["get_dimensions_agent"],
                "get_entities": self.tool_agents["get_entities_agent"],
                "query_metrics": self.tool_agents["query_metrics_agent"],
                "tableau": self.tool_agents["tableau_agent"],
                "snowflake": self.tool_agents["snowflake_agent"],
                "manager": self.agents["data_manager"],
                "reporting": self.agents["data_analyst"],
                "security": self.agents["data_analyst"],  # Fallback to data_analyst
            }
            selected_agent = agent_mapping.get(agent, self.agents["data_analyst"])
        else:
            # Default to data analyst
            selected_agent = self.agents["data_analyst"]
        
        try:
            # Run the selected agent
            result = await Runner().run(selected_agent, user_message)
            
            # Convert result to Message format
            if hasattr(result, 'final_output'):
                content = result.final_output
            else:
                content = str(result)
            
            return Message(role="assistant", content=content)
            
        except Exception as e:
            logger.error(f"Error processing request with agent {agent}: {e}")
            return Message(
                role="assistant", 
                content=f"I encountered an error while processing your request: {str(e)}"
            )


if __name__ == "__main__":
    # Example usage
    agents = get_agents()
    print("Available agents:", list(agents.keys()))
    
    tool_agents = get_tool_agents()
    print("Available tool agents:", list(tool_agents.keys()))
    
    # Display agent capabilities
    analyst = agents["data_analyst"]
    print(f"Data Analyst tools: {len(analyst.tools)}")
    print(f"Data Analyst handoffs: {len(analyst.handoffs)}")
    print(f"Data Analyst guardrails: {len(analyst.output_guardrails)}")
