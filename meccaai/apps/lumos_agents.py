"""Redesigned Multi-agent system for LumosAI with 3 specialized agents using OpenAI Agent SDK."""

from typing import Any

from agents import (
    Agent,
    GuardrailFunctionOutput,
    handoff,
    input_guardrail,
    output_guardrail,
    Runner,
    FunctionTool,
)

import json

from meccaai.adapters.openai_sdk.runner import OpenAIRunner
from meccaai.adapters.openai_sdk.tool_adapter import tools_to_openai_functions
from meccaai.core.config import get_settings
from meccaai.core.logging import get_logger
from meccaai.core.tool_registry import get_registry
from meccaai.core.types import AgentDecision, AgentResponse, Message

logger = get_logger(__name__)


@input_guardrail
def check_input_safety(context, agent, input):
    """Input guardrail to check for PII and sensitive data."""
    input_lower = input.lower()

    # Check for PII patterns
    pii_indicators = [
        "medicare",
        "ssn",
        "credit card",
        "passport",
        "driver license",
        "bank account",
        "routing number",
        "personal id",
        "national id",
    ]

    # Check for sensitive data patterns
    sensitive_indicators = [
        "password",
        "secret",
        "confidential",
        "restricted",
        "classified",
    ]

    detected_pii = [
        indicator for indicator in pii_indicators if indicator in input_lower
    ]
    detected_sensitive = [
        indicator for indicator in sensitive_indicators if indicator in input_lower
    ]

    if detected_pii or detected_sensitive:
        logger.warning(
            f"PII/sensitive data detected: PII={detected_pii}, Sensitive={detected_sensitive}"
        )
        return GuardrailFunctionOutput(
            output_info={
                "pii_detected": detected_pii,
                "sensitive_detected": detected_sensitive,
                "blocked": True,
            },
            tripwire_triggered=True,
        )

    logger.info("Input safety check passed")
    return GuardrailFunctionOutput(
        output_info={"safety_check": "passed", "blocked": False},
        tripwire_triggered=False,
    )


@output_guardrail
def validate_output_quality(context, agent, agent_output):
    """Output guardrail to validate response quality and safety."""
    output_lower = agent_output.lower()

    # Check for data leakage
    leak_indicators = ["password", "secret", "confidential", "private"]

    detected_leaks = [
        indicator for indicator in leak_indicators if indicator in output_lower
    ]

    if detected_leaks:
        logger.warning(f"Potential data leakage detected: {detected_leaks}")
        return GuardrailFunctionOutput(
            output_info={"leakage_detected": detected_leaks, "blocked": True},
            tripwire_triggered=True,
        )

    # Check for minimum quality standards
    if len(agent_output.strip()) < 10:
        logger.warning("Output too short, may indicate poor quality")
        return GuardrailFunctionOutput(
            output_info={
                "quality_issue": "output_too_short",
                "length": len(agent_output.strip()),
            },
            tripwire_triggered=True,
        )

    logger.info("Output quality validation passed")
    return GuardrailFunctionOutput(
        output_info={"quality_check": "passed"}, tripwire_triggered=False
    )


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

    async def process_message(self, messages: list[Message]) -> AgentResponse:
        """Process a message using this agent's capabilities."""
        # Add system message with agent role
        system_message = Message(
            role="system",
            content=f"You are {self.name}, {self.role}. "
            f"Use the available tools to help with the user's request. "
            f"Be professional, accurate, and helpful in your responses.\\n\\n"
            f"IMPORTANT: When using tools, convert human language into the correct data types:\\n"
            f"- If a tool expects a list parameter and the user mentions items in natural language, convert them to a proper list format\\n"
            f"- If a tool expects specific parameter types (strings, integers, booleans), interpret the user's intent and convert appropriately\\n"
            f"- For example: 'show me sales metrics' should convert 'sales metrics' to ['sales_metrics'] if the tool expects a list\\n"
            f"- For example: 'query the revenue metric' should convert 'revenue metric' to ['revenue'] if that's the actual metric name\\n"
            f"- Always match parameter names and types to what the tools actually expect\\n"
            f"- If you're unsure about exact metric names or parameter values, use list_metrics or similar discovery tools first\\n\\n"
            f"CRITICAL - HANDOFF DECISION:\\n"
            f"At the end of your response, you MUST indicate whether the task is complete or should continue to the next agent:\\n"
            f"- Add '[DECISION: COMPLETE]' if you have fully answered the user's question and no further agents are needed\\n"
            f"- Add '[DECISION: CONTINUE]' if the task requires additional processing by the next agent in the chain\\n"
            f"- GUARDRAIL AGENT RULE: You should ALWAYS use '[DECISION: CONTINUE]' unless the request is blocked for security reasons\\n"
            f"- DATA AGENTS RULE: Use '[DECISION: COMPLETE]' when you have provided the actual data requested\\n"
            f"- Always include a decision tag at the very end of your response",
        )

        agent_messages = [system_message] + messages

        # Track tools that might be used
        tools_used = []

        # Custom runner that tracks tool usage
        response = await self._run_with_tool_tracking(agent_messages, tools_used)

        # Format response with agent name and tool information
        formatted_response = self._format_response(response, tools_used)

        # Parse the decision from the response
        decision = self._parse_decision(formatted_response.content or "")
        logger.info(
            f"{self.name} decision: continue={decision.continue_chain}, reason='{decision.reason}', confidence={decision.confidence}"
        )

        return AgentResponse(
            message=formatted_response, decision=decision, agent_name=self.name
        )

    def _parse_decision(self, content: str) -> AgentDecision:
        """Parse the agent's decision from their response content."""
        content_lower = content.lower()
        logger.info(
            f"[DEBUG] {self.name} parsing decision from content: {content_lower[:200]}..."
        )

        if "[decision: complete]" in content_lower:
            return AgentDecision(
                continue_chain=False,
                reason="Agent indicated task is complete",
                confidence=1.0,
            )
        elif "[decision: continue]" in content_lower:
            return AgentDecision(
                continue_chain=True,
                reason="Agent indicated task should continue to next agent",
                confidence=1.0,
            )
        else:
            # Default decision based on agent behavior analysis
            # If no explicit decision, try to infer from content
            completion_indicators = [
                "task complete",
                "finished",
                "final answer",
                "here is the result",
                "query complete",
                "analysis complete",
            ]

            continue_indicators = [
                "will now",
                "proceeding to",
                "next step",
                "handoff to",
                "continue with",
                "now, i will",
                "i will proceed",
                "let's",
                "first, i will",
                "now i will",
                "let me check",
                "i will check",
                "retrieve the",
                "get the",
                "first, let me",
                "first i will",
                "will proceed to",
            ]

            has_completion = any(
                indicator in content_lower for indicator in completion_indicators
            )
            has_continue = any(
                indicator in content_lower for indicator in continue_indicators
            )

            logger.info(
                f"[DEBUG] {self.name} completion indicators found: {has_completion}"
            )
            logger.info(
                f"[DEBUG] {self.name} continue indicators found: {has_continue}"
            )
            if has_continue:
                found_indicators = [
                    ind for ind in continue_indicators if ind in content_lower
                ]
                logger.info(
                    f"[DEBUG] {self.name} found continue indicators: {found_indicators}"
                )

            if has_completion and not has_continue:
                return AgentDecision(
                    continue_chain=False,
                    reason="Inferred completion from response content",
                    confidence=0.7,
                )
            elif has_continue and not has_completion:
                return AgentDecision(
                    continue_chain=True,
                    reason="Inferred continuation from response content",
                    confidence=0.7,
                )
            else:
                # Special handling for Guardrail Agent - should almost always continue unless blocked
                if self.name == "Guardrail Agent":
                    block_indicators = [
                        "blocked",
                        "denied",
                        "unauthorized",
                        "violation",
                        "restricted",
                        "forbidden",
                        "cannot proceed",
                        "reject",
                        "pii detected",
                        "sensitive data found",
                        "privacy violation",
                    ]
                    is_blocked = any(
                        indicator in content_lower for indicator in block_indicators
                    )

                    return AgentDecision(
                        continue_chain=not is_blocked,
                        reason="Guardrail agent default: continue unless blocked",
                        confidence=0.8,
                    )

                # Default to continue for most agents, except if this is clearly an error
                error_indicators = ["error", "failed", "cannot", "access denied"]
                has_error = any(
                    indicator in content_lower for indicator in error_indicators
                )

                return AgentDecision(
                    continue_chain=not has_error,
                    reason="Default decision based on error analysis",
                    confidence=0.5,
                )

    async def _run_with_tool_tracking(
        self, messages: list[Message], tools_used: list[str]
    ) -> Message:
        """Run conversation with tool tracking."""
        # Create a custom runner instance to track tool calls
        original_execute_tool_call = self.runner._execute_tool_call

        async def tracked_execute_tool_call(tool_call, available_tools):
            # Track the tool being used
            tools_used.append(tool_call.function.name)
            return await original_execute_tool_call(tool_call, available_tools)

        # Temporarily replace the method
        self.runner._execute_tool_call = tracked_execute_tool_call

        try:
            return await self.runner.run_conversation(
                messages=messages, tools=self.tools, model=self.model
            )
        finally:
            # Restore original method
            self.runner._execute_tool_call = original_execute_tool_call

    def _format_response(self, response: Message, tools_used: list[str]) -> Message:
        """Format response with agent name and tool information."""
        # Create header with agent info
        header = f"**🤖 Agent: {self.name}**"

        if tools_used:
            tools_str = ", ".join(set(tools_used))  # Remove duplicates
            header += f"\\n**🔧 Tools Used: {tools_str}**"
        else:
            header += "\\n**🔧 Tools Used: None**"

        header += "\\n\\n---\\n\\n"

        # Combine header with actual response
        formatted_content = header + (response.content or "")

        return Message(role=response.role, content=formatted_content)


# GuardrailAgent removed - guardrails now integrated into DataAnalyst agent


class DataAnalyst(LumosAgent):
    """Specialized agent for data analysis with access to dbt, tableau, cortex, and reporting tools."""

    def __init__(self):
        super().__init__(
            name="Data Analyst",
            role="a comprehensive data analyst who helps with data queries, transformations, visualizations, "
            "and analytics. I have access to dbt for data transformations, Tableau for visualizations, "
            "Cortex for AI-powered insights, and reporting tools. I can help you run dbt commands, "
            "manage data transformations, query metrics, explore models, generate SQL from natural language, "
            "create visualizations, and generate comprehensive reports. When tasks require workflow automation "
            "or project management, I hand off to the Data Manager.",
            tools=[
                # Introduction tool
                "self_intro",
                # dbt CLI tools
                "build",
                "compile",
                "docs",
                "list",
                "parse",
                "run",
                "test",
                "show",
                # Semantic Layer tools
                "list_metrics",
                "get_dimensions",
                "get_entities",
                "query_metrics",
                "get_metrics_compiled_sql",
                # Discovery tools
                "get_mart_models",
                "get_all_models",
                "get_model_details",
                "get_model_parents",
                "get_model_children",
                # SQL tools
                "text_to_sql",
                "execute_sql",
                # Tableau tools
                "list_all_pats",
                "get_view",
                "query_view_pdf",
                "list_views",
                # Cortex tools
                "run_cortex_agents",
            ],
            model="gpt-4o-mini",
        )

        # Setup SDK Agent with guardrails
        self._setup_sdk_agent()

    def _setup_sdk_agent(self):
        """Setup the OpenAI Agent SDK agent with proper guardrails."""
        settings = get_settings()

        # Set OpenAI API key for the agents package
        import os

        if hasattr(settings, "openai_api_key") and settings.openai_api_key:
            os.environ["OPENAI_API_KEY"] = settings.openai_api_key

        # Get tools from registry and convert to agents package format
        registry = get_registry()
        all_tools = registry.list_tools()

        # Filter tools for this agent
        agent_tool_names = [
            "self_intro",
            "build",
            "compile",
            "docs",
            "list",
            "parse",
            "run",
            "test",
            "show",
            "list_metrics",
            "get_dimensions",
            "get_entities",
            "query_metrics",
            "get_metrics_compiled_sql",
            "get_mart_models",
            "get_all_models",
            "get_model_details",
            "get_model_parents",
            "get_model_children",
            "text_to_sql",
            "execute_sql",
            "list_all_pats",
            "get_view",
            "query_view_pdf",
            "list_views",
            "run_cortex_agents",
        ]
        filtered_tools = [tool for tool in all_tools if tool.name in agent_tool_names]

        # Convert to agents package FunctionTool format
        agent_tools = []
        for tool in filtered_tools:

            def create_tool_wrapper(original_tool):
                async def tool_wrapper(context, tool_input):
                    try:
                        # Parse the tool input JSON
                        kwargs = json.loads(tool_input) if tool_input else {}
                        
                        # Simple parameter conversion for tools that expect lists  
                        if original_tool.name in ["get_dimensions", "get_entities"] and "metrics" in kwargs:
                            # Only convert metrics parameter if it's a string (for backwards compatibility)
                            if isinstance(kwargs["metrics"], str):
                                # Map common user terms to actual metric names
                                metric_str = kwargs["metrics"].lower()
                                if "trade" in metric_str:
                                    kwargs["metrics"] = ["met_trade_sale_item_sale_extended_price_aud"]
                                elif "sales" in metric_str or "sale" in metric_str:
                                    kwargs["metrics"] = ["met_trade_sale_item_sale_extended_price_aud"]
                                elif "finance" in metric_str:
                                    kwargs["metrics"] = ["met_finance_gl_reported_margin_aud"]
                                elif "compliance" in metric_str:
                                    kwargs["metrics"] = ["met_compliance_cleansed_item_size"]
                                else:
                                    # Default: wrap string in list
                                    kwargs["metrics"] = [kwargs["metrics"]]
                        
                        result = await original_tool.call(**kwargs)
                        return (
                            result.result if hasattr(result, "result") else str(result)
                        )
                    except Exception as e:
                        return f"Error calling {original_tool.name}: {str(e)}"

                return tool_wrapper

            agent_tools.append(
                FunctionTool(
                    name=tool.name,
                    description=tool.description,
                    params_json_schema=tool.parameters,
                    on_invoke_tool=create_tool_wrapper(tool),
                )
            )

        logger.info(
            f"Data Analyst agent has {len(agent_tools)} tools available: {[t.name for t in agent_tools]}"
        )

        # Create the agent with input and output guardrails and tools
        try:
            self.sdk_agent = Agent(
                name="data_analyst",
                model=settings.models.openai.model,
                instructions=(
                    f"You are {self.name}, {self.role}. "
                    "You have built-in security guardrails that check for PII and sensitive data. "
                    "IMPORTANT: When users ask about who you are or request an introduction, use the 'self_intro' tool. "
                    "When users ask about available metrics, use the 'list_metrics' tool. "
                    "Always use appropriate tools when they are available for the user's request. "
                    "Provide complete data analysis with actual numerical results. "
                    "When tasks require workflow automation or project management, hand off to the Data Manager.\n\n"
                    "CRITICAL - PARAMETER CONVERSION RULES:\n"
                    "1. For tools expecting list parameters (like get_dimensions, query_metrics):\n"
                    "   - Convert user keywords to metric names: 'trade' should become ['met_trade_sale_item_sale_extended_price_aud'] or similar trade-related metrics\n"
                    "   - For 'trade': use ['met_trade_sale_item_sale_extended_price_aud', 'met_trade_last_year_physical_traffic_quantity']\n"
                    "   - For 'sales': use metrics containing 'sale' in their names\n"
                    "   - Never pass raw strings like 'trade' - always convert to actual metric names in list format\n"
                    "2. For query_metrics WHERE clauses - ALWAYS use FULL dimension paths:\n"
                    "   - CORRECT: {{ Dimension('sales_channel__sales_channel_code') }} = 'L098'\n"
                    "   - WRONG: {{ Dimension('sales_channel_code') }} = 'L098'\n"
                    "   - CORRECT: {{ Dimension('item__brand_name') }} = 'Nike'\n"
                    "   - CORRECT: {{ TimeDimension('date_key__date', 'DAY') }} >= '2024-01-01'\n"
                    "3. Known metric examples to use:\n"
                    "   - Trade metrics: ['met_trade_sale_item_sale_extended_price_aud', 'met_trade_last_year_physical_traffic_quantity']\n"
                    "   - Finance metrics: ['met_finance_gl_reported_margin_aud']\n"
                    "   - Compliance metrics: ['met_compliance_cleansed_item_size', 'met_compliance_concentration_percentage']\n"
                    "4. Be efficient - avoid excessive tool chaining. Use your knowledge of common metric patterns."
                ),
                tools=agent_tools,
                input_guardrails=[check_input_safety],
                output_guardrails=[validate_output_quality],
            )
        except Exception as e:
            logger.error(f"Error creating Data Analyst agent: {e}")
            # Fallback without tools
            self.sdk_agent = Agent(
                name="data_analyst",
                model=settings.models.openai.model,
                instructions=f"You are {self.name}, {self.role}.",
                input_guardrails=[check_input_safety],
                output_guardrails=[validate_output_quality],
            )

    async def process_message(self, messages: list[Message]) -> AgentResponse:
        """Process a message with data analysis-specific guidance."""
        # Add system message with enhanced data analysis guidance
        system_message = Message(
            role="system",
            content=f"You are {self.name}, {self.role}. "
            f"Use the available tools to help with the user's request. "
            f"Be professional, accurate, and helpful in your responses.\\n\\n"
            f"CRITICAL - PARAMETER CONVERSION RULES:\\n"
            f"When users ask about metrics in natural language, you MUST convert their requests to proper data types:\\n\\n"
            f"1. For query_metrics tool:\\n"
            f"   - 'metrics' parameter expects list[str] - ALWAYS convert metric names to a list\\n"
            f"   - Example: 'show me sales metrics' → metrics=['sales_metric_name']\\n"
            f"   - Example: 'query revenue data' → metrics=['revenue_related_metric_name']\\n\\n"
            f"2. For get_dimensions tool:\\n"
            f"   - 'metrics' parameter expects list[str] - convert to list format\\n\\n"
            f"3. IMPORTANT WORKFLOW:\\n"
            f"   - If unsure about exact metric names, ALWAYS use list_metrics FIRST to discover available metrics\\n"
            f"   - Match user's natural language to actual metric names from list_metrics\\n"
            f"   - Then use the correct metric names in list format for query_metrics\\n\\n"
            f"4. NEVER pass raw strings where lists are expected\\n"
            f"5. ALWAYS convert human language to proper tool parameter formats\\n\\n"
            f"TASK COMPLETION REQUIREMENTS:\\n"
            f"- ALWAYS complete the full task the user requested in a SINGLE response\\n"
            f"- If the user asks for specific data (like 'total sales for channel L098'), provide the actual numerical answer\\n"
            f"- WORKFLOW: Use list_metrics first, then immediately use query_metrics with proper filters\\n"
            f"- Don't stop after just listing metrics - that's only step 1 of 2\\n"
            f"- Example full workflow:\\n"
            f"  1. Use list_metrics to find relevant metrics\\n"
            f"  2. Use query_metrics with the metric name and where filters for the specific data requested\\n"
            f"- CRITICAL: Your response must contain the actual data the user asked for, not just preparation steps\\n"
            f"- Use tools multiple times in one response as needed to get the final answer\\n\\n"
            f"HANDOFF RULES:\\n"
            f"- Use '[DECISION: CONTINUE]' if the task requires workflow automation, project management, or Jira/Confluence operations\\n"
            f"- Use '[DECISION: COMPLETE]' if you have successfully provided all the data/analysis requested\\n"
            f"- Always include a decision tag at the very end of your response",
        )

        agent_messages = [system_message] + messages

        # Track tools that might be used
        tools_used = []

        # Custom runner that tracks tool usage
        response = await self._run_with_tool_tracking(agent_messages, tools_used)

        # Format response with agent name and tool information
        formatted_response = self._format_response(response, tools_used)

        # Parse the decision from the response
        decision = self._parse_decision(formatted_response.content or "")

        return AgentResponse(
            message=formatted_response, decision=decision, agent_name=self.name
        )


class DataManager(LumosAgent):
    """Specialized agent for workflow automation and project management."""

    def __init__(self):
        super().__init__(
            name="Data Manager",
            role="a workflow automation and project management specialist who handles "
            "Zapier integrations, Jira ticket management, Confluence documentation, and "
            "process automation. I can help you create tickets, update projects, manage workflows, "
            "and integrate various systems through Zapier automations.",
            tools=[
                # Jira/Confluence MCP tools
                "search_issues",
                "get_epic_children",
                "get_issue",
                "create_issue",
                "update_issue",
                "add_attachment",
                "add_comment",
                # Zapier MCP tools (dynamic - discovered at runtime based on user's Zapier config)
                # Note: Zapier tools are dynamic and discovered at runtime
            ],
            model="gpt-4o-mini",
        )

        # Setup OpenAI Agent SDK agent
        self._setup_sdk_agent()

    def _setup_sdk_agent(self):
        """Setup the OpenAI Agent SDK agent with proper guardrails."""
        settings = get_settings()

        # Set OpenAI API key for the agents package
        import os

        if hasattr(settings, "openai_api_key") and settings.openai_api_key:
            os.environ["OPENAI_API_KEY"] = settings.openai_api_key

        # Get tools from registry and convert to agents package format
        registry = get_registry()
        all_tools = registry.list_tools()

        # Filter tools for this agent
        agent_tool_names = [
            "search_issues",
            "get_epic_children",
            "get_issue",
            "create_issue",
            "update_issue",
            "add_attachment",
            "add_comment",
        ]
        filtered_tools = [tool for tool in all_tools if tool.name in agent_tool_names]

        # Convert to agents package FunctionTool format
        agent_tools = []
        for tool in filtered_tools:

            def create_tool_wrapper(original_tool):
                async def tool_wrapper(context, tool_input):
                    try:
                        # Parse the tool input JSON
                        kwargs = json.loads(tool_input) if tool_input else {}
                        
                        # Data Manager doesn't need metrics conversion but keeping consistency
                        result = await original_tool.call(**kwargs)
                        return (
                            result.result if hasattr(result, "result") else str(result)
                        )
                    except Exception as e:
                        return f"Error calling {original_tool.name}: {str(e)}"

                return tool_wrapper

            agent_tools.append(
                FunctionTool(
                    name=tool.name,
                    description=tool.description,
                    params_json_schema=tool.parameters,
                    on_invoke_tool=create_tool_wrapper(tool),
                )
            )

        logger.info(
            f"Data Manager agent has {len(agent_tools)} tools available: {[t.name for t in agent_tools]}"
        )

        # Create the agent with output guardrails and tools
        try:
            self.sdk_agent = Agent(
                name="data_manager",
                model=settings.models.openai.model,
                instructions=(
                    f"You are {self.name}, {self.role}. "
                    "Always use appropriate tools when they are available for the user's request. "
                    "Handle workflow automation and project management tasks efficiently."
                ),
                tools=agent_tools,
                output_guardrails=[validate_output_quality],
            )
        except Exception as e:
            logger.error(f"Error creating Data Manager agent: {e}")
            # Fallback without tools
            self.sdk_agent = Agent(
                name="data_manager",
                model=settings.models.openai.model,
                instructions=f"You are {self.name}, {self.role}.",
                output_guardrails=[validate_output_quality],
            )


class LumosAIOrchestrator(LumosAgent):
    """Main orchestrating agent that coordinates the 3 specialized agents."""

    def __init__(self):
        super().__init__(
            name="Lumos AI Orchestrator",
            role="the central orchestrator who manages the input guardrails and coordinates "
            "between the Guardrail Agent, Data Analyst, and Data Manager. I ensure proper "
            "security scanning and route tasks to the appropriate specialized agents.",
            tools=["self_intro"],
            model="gpt-4o-mini",
        )

        # Initialize the 2 main agents (guardrails are integrated into DataAnalyst)
        self.data_analyst = DataAnalyst()
        self.data_manager = DataManager()

    def _setup_handoffs(self):
        """Setup agent handoffs using OpenAI Agent SDK patterns."""

        # Create handoff from data analyst to data manager
        self.analyst_to_manager_handoff = handoff(
            agent=self.data_manager.sdk_agent,
            tool_name_override="hand_off_to_data_manager",
            tool_description_override="Hand off to the Data Manager for workflow automation and project management",
        )

        # Note: In the OpenAI Agent SDK, handoffs are automatically made available as tools


class LumosAgentSystem:
    """Main system for managing the redesigned Lumos 3-agent environment."""

    def __init__(self):
        self.orchestrator = LumosAIOrchestrator()
        self.agents = {
            "orchestrator": self.orchestrator,
            "data_analyst": self.orchestrator.data_analyst,
            "data_manager": self.orchestrator.data_manager,
        }

        # Setup SDK handoffs
        self.orchestrator._setup_handoffs()

    async def process_with_sdk_agent(
        self, agent_name: str, messages: list[Message]
    ) -> Message:
        """Process request using OpenAI Agent SDK with automatic handoffs."""

        # Convert messages to OpenAI format
        openai_messages = [
            {"role": msg.role, "content": msg.content} for msg in messages
        ]

        # Get the starting agent
        if agent_name == "data_analyst":
            current_agent = self.agents["data_analyst"].sdk_agent
        elif agent_name == "data_manager":
            current_agent = self.agents["data_manager"].sdk_agent
        else:
            logger.warning(f"Unknown agent: {agent_name}, using data_analyst agent")
            current_agent = self.agents["data_analyst"].sdk_agent

        try:
            # Use Runner to execute the agent
            runner = Runner()

            # Convert messages to input string (for simplicity, using the last message)
            input_text = messages[-1].content if messages else "Hello"

            # Run the agent (OpenAI Agent SDK will handle guardrails and handoffs automatically)
            logger.info(f"Running SDK agent '{current_agent.name}' with {len(current_agent.tools)} tools")
            response = await runner.run(
                starting_agent=current_agent, input=input_text, context=None
            )
            logger.info(f"SDK agent response type: {type(response)}")
            logger.info(f"SDK agent raw_responses count: {len(response.raw_responses) if hasattr(response, 'raw_responses') else 'N/A'}")

            # Extract tools used from the response
            tools_used = self._extract_tools_from_response(response)

            # Format the response with tool information
            formatted_content = self._format_response_with_tools(
                str(response.final_output)
                if response.final_output
                else "No response generated",
                tools_used,
                current_agent.name,
            )

            return Message(
                role="assistant",
                content=formatted_content,
            )

        except Exception as e:
            logger.error(f"OpenAI Agent SDK execution error: {e}")
            return Message(
                role="assistant", content=f"Error processing request: {str(e)}"
            )

    def _extract_tools_from_response(self, response) -> list[str]:
        """Extract tool names used during agent execution from RunResult."""
        tools_used = []

        # Check raw_responses for any tool calls (most reliable method)
        for raw_response in response.raw_responses:
            if hasattr(raw_response, "tool_calls") and raw_response.tool_calls:
                for tool_call in raw_response.tool_calls:
                    if hasattr(tool_call, "function") and hasattr(
                        tool_call.function, "name"
                    ):
                        tools_used.append(tool_call.function.name)

        # If no tool calls detected, check response content for known tool signatures
        if not tools_used:
            final_output_str = (
                str(response.final_output) if response.final_output else ""
            )

            # Check for self_intro tool signature
            if any(
                phrase in final_output_str
                for phrase in ["Mecca Data team", "Lumos_AI", "created by"]
            ):
                tools_used.append("self_intro")

        return list(set(tools_used))  # Remove duplicates

    def _format_response_with_tools(
        self, content: str, tools_used: list[str], agent_name: str
    ) -> str:
        """Format response with agent name and tool information."""
        # Create header with agent info
        header = f"**🤖 Agent: {agent_name}**"

        if tools_used:
            tools_str = ", ".join(tools_used)
            header += f"\n**🔧 Tools Used: {tools_str}**"
        else:
            header += "\n**🔧 Tools Used: None (responded without tool calls)**"

        header += "\n\n---\n\n"

        # Combine header with actual response
        return header + content

    def _extract_content_without_header(self, content: str) -> str:
        """Extract content without the agent header for internal chain processing."""
        # Remove the agent header formatting for cleaner internal communication
        if "---" in content:
            parts = content.split("---", 1)
            if len(parts) > 1:
                return parts[1].strip()
        return content

    async def process_request(
        self, messages: list[Message], agent: str | None = None
    ) -> Message:
        """Process a request using OpenAI SDK agents with automatic handoffs."""

        settings = get_settings()

        # If specific agent requested, use it directly
        if agent and agent in self.agents:
            logger.info(f"Direct agent request: using {agent} agent")
            if hasattr(self.agents[agent], "sdk_agent"):
                return await self.process_with_sdk_agent(agent, messages)
            else:
                # Fallback to legacy processing
                agent_response = await self.agents[agent].process_message(messages)
                return agent_response.message

        # Default to data_analyst with SDK agents if auto handoff enabled
        if settings.agents.auto_handoff:
            logger.info(
                "Using SDK data_analyst processing with automatic handoffs (includes input guardrails)"
            )
            return await self.process_with_sdk_agent("data_analyst", messages)

        # Use orchestrator by default if auto handoff is disabled
        orchestrator_response = await self.orchestrator.process_message(messages)
        return orchestrator_response.message

    def list_agents(self) -> dict[str, str]:
        """List all available agents and their roles."""
        return {name: agent.role for name, agent in self.agents.items()}


async def main():
    """Example usage of the redesigned Lumos Agent System."""
    system = LumosAgentSystem()

    # Example: Data query (should go through guardrail -> data_analyst)
    messages = [
        Message(
            role="user", content="What is the total sales for sales channel code L098?"
        )
    ]

    result = await system.process_request(messages)
    print(f"Data Analysis Result: {result.content}")

    # Example: Workflow request (should go through guardrail -> data_analyst -> data_manager)
    workflow_messages = [
        Message(
            role="user",
            content="Create a Jira ticket for the sales analysis we just did and set up a Zapier automation",
        )
    ]

    workflow_result = await system.process_request(workflow_messages)
    print(f"Workflow Result: {workflow_result.content}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
