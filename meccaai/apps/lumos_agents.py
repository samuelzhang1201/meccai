"""Multi-agent system for LumosAI with specialized agents."""

from meccaai.adapters.openai_sdk.runner import OpenAIRunner
from meccaai.core.logging import get_logger
from meccaai.core.tool_registry import get_registry
from meccaai.core.types import Message

logger = get_logger(__name__)


class LumosAgent:
    """Base class for specialized agents in the Lumos system."""

    def __init__(
        self,
        name: str,
        role: str,
        tools: list[str] | None = None,
        model: str = "gpt-4o-mini",
    ):
        self.name = name
        self.role = role
        self.model = model
        self.runner = OpenAIRunner()
        self.registry = get_registry()

        # Get specified tools or all tools
        if tools:
            self.tools = [
                tool for tool in self.registry.list_tools() if tool.name in tools
            ]
        else:
            self.tools = self.registry.list_tools()

    async def process_message(self, messages: list[Message]) -> Message:
        """Process a message using this agent's capabilities."""
        # Add system message with agent role
        system_message = Message(
            role="system",
            content=f"You are {self.name}, {self.role}. "
            f"Use the available tools to help with the user's request. "
            f"Be professional, accurate, and helpful in your responses.",
        )

        agent_messages = [system_message] + messages

        return await self.runner.run_conversation(
            messages=agent_messages, tools=self.tools, model=self.model
        )


class TableauAnalyst(LumosAgent):
    """Specialized agent for Tableau data visualization and analytics."""

    def __init__(self):
        super().__init__(
            name="Tableau Analyst",
            role="an expert data visualization specialist who helps users work with "
            "Tableau dashboards, views, and reports. I can help you query views, "
            "export PDFs, manage PATs, and analyze visualization data.",
            tools=["list_all_pats", "get_view", "query_view_pdf", "list_views"],
            model="gpt-4o-mini",
        )


class DBTBuildAgent(LumosAgent):
    """Specialized agent for dbt (data build tool) operations."""

    def __init__(self):
        super().__init__(
            name="DBT Build Agent",
            role="a data engineering specialist who helps with dbt model building, "
            "testing, and deployment. I can help you run dbt commands, "
            "manage data transformations, and ensure data quality.",
            tools=["dbt_run", "dbt_test", "dbt_docs_generate"],
            model="gpt-4o-mini",
        )


class ReportingAnalyst(LumosAgent):
    """Specialized agent for data analysis and reporting."""

    def __init__(self):
        super().__init__(
            name="Reporting Analyst",
            role="an experienced data analyst who helps analyze data patterns, "
            "create insights, and generate comprehensive reports. I can help "
            "you interpret data, identify trends, and communicate findings effectively.",
            tools=[],  # Uses general-purpose tools for analysis
            model="gpt-4o-mini",
        )


class SecurityAnalyst(LumosAgent):
    """Specialized agent for security analysis and prompt scanning."""

    def __init__(self):
        super().__init__(
            name="Security Analyst",
            role="a cybersecurity specialist who analyzes user requests for potential "
            "security risks, scans prompts for sensitive data requests, and ensures "
            "data protection compliance. I help identify and prevent unauthorized "
            "access to sensitive information like PII, financial data, and proprietary content.",
            tools=["prompt_scanner"],
            model="gpt-4o-mini",
        )


class LumosAIManager(LumosAgent):
    """Main orchestrating agent that coordinates other agents and handles workflows."""

    def __init__(self):
        super().__init__(
            name="Lumos AI Manager",
            role="the central orchestrator who coordinates between specialized agents, "
            "generates comprehensive reports, and manages communication workflows. "
            "I can delegate tasks to other agents and combine their outputs into "
            "cohesive deliverables.",
            tools=[
                "send_email",
                "create_slack_message",
                "create_google_sheet_row",
                "trigger_webhook",
                "self_intro",
            ],
            model="gpt-4o-mini",
        )

        # Initialize specialized agents
        self.tableau_analyst = TableauAnalyst()
        self.dbt_build = DBTBuildAgent()
        self.reporting_analyst = ReportingAnalyst()
        self.security_analyst = SecurityAnalyst()

    async def delegate_to_agent(
        self, agent_name: str, messages: list[Message]
    ) -> Message:
        """Delegate a task to a specialized agent."""
        agent_map = {
            "tableau": self.tableau_analyst,
            "dbt": self.dbt_build,
            "reporting": self.reporting_analyst,
            "security": self.security_analyst,
        }

        agent = agent_map.get(agent_name.lower())
        if not agent:
            return Message(
                role="assistant",
                content=f"Unknown agent: {agent_name}. Available agents: {list(agent_map.keys())}",
            )

        logger.info(f"Delegating task to {agent.name}")
        return await agent.process_message(messages)

    async def orchestrate_workflow(
        self, task: str, messages: list[Message]
    ) -> list[Message]:
        """Orchestrate a complex workflow involving multiple agents."""
        results = []

        # Analyze the task to determine which agents to involve
        task_lower = task.lower()

        if (
            "tableau" in task_lower
            or "visualization" in task_lower
            or "dashboard" in task_lower
        ):
            tableau_result = await self.tableau_analyst.process_message(messages)
            results.append(tableau_result)

        if "dbt" in task_lower or "transform" in task_lower or "model" in task_lower:
            dbt_result = await self.dbt_build.process_message(messages)
            results.append(dbt_result)

        if (
            "analysis" in task_lower
            or "report" in task_lower
            or "insight" in task_lower
        ):
            # Pass results from other agents to reporting analyst
            enhanced_messages = messages + results
            reporting_result = await self.reporting_analyst.process_message(
                enhanced_messages
            )
            results.append(reporting_result)

        return results


class LumosAgentSystem:
    """Main system for managing the Lumos multi-agent environment."""

    def __init__(self):
        self.manager = LumosAIManager()
        self.agents = {
            "manager": self.manager,
            "tableau": self.manager.tableau_analyst,
            "dbt": self.manager.dbt_build,
            "reporting": self.manager.reporting_analyst,
            "security": self.manager.security_analyst,
        }

    async def process_request(
        self, messages: list[Message], agent: str | None = None, workflow: bool = False
    ) -> Message | list[Message]:
        """Process a request using the appropriate agent or workflow."""

        if workflow:
            # Use orchestrated workflow
            task = messages[-1].content if messages else ""
            return await self.manager.orchestrate_workflow(task, messages)

        if agent and agent in self.agents:
            # Use specific agent
            return await self.agents[agent].process_message(messages)

        # Use manager by default
        return await self.manager.process_message(messages)

    def list_agents(self) -> dict[str, str]:
        """List all available agents and their roles."""
        return {name: agent.role for name, agent in self.agents.items()}


async def main():
    """Example usage of the Lumos Agent System."""
    system = LumosAgentSystem()

    # Example: Query Tableau
    messages = [
        Message(
            role="user", content="List all personal access tokens in our Tableau site"
        )
    ]

    result = await system.process_request(messages, agent="tableau")
    if isinstance(result, Message):
        print(f"Tableau Agent Result: {result.content}")
    else:
        print(f"Tableau Agent Results: {len(result)} responses")

    # Example: Orchestrated workflow
    workflow_messages = [
        Message(
            role="user",
            content="Create a comprehensive report on our Tableau usage and export key dashboards",
        )
    ]

    workflow_results = await system.process_request(workflow_messages, workflow=True)
    if isinstance(workflow_results, list):
        print(f"Workflow Results: {len(workflow_results)} responses")
    else:
        print(f"Workflow Result: {workflow_results.content}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
