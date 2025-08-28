"""Gradio web interface for Lumos AI Bedrock Agent System."""

import asyncio
import json
from datetime import datetime
from typing import List, Tuple

import gradio as gr

from meccaai.apps.lumos_bedrock_agents import LumosBedrockAgentSystem
from meccaai.core.conversation_logger import get_conversation_logger
from meccaai.core.logging import get_logger
from meccaai.core.types import Message

logger = get_logger(__name__)


class GradioBedrockApp:
    """Gradio web interface for the Bedrock agent system."""

    def __init__(self):
        """Initialize the Gradio app."""
        self.system = LumosBedrockAgentSystem()
        self.conversation_history = []
        self.current_tool_calls = []  # Track current conversation's tool calls

    async def chat(
        self, message: str, history: List[dict], agent_choice: str
    ) -> Tuple[List[dict], str, str]:
        """Process a chat message and return updated history and tool calls."""
        if not message.strip():
            return history, "", self.get_current_tool_calls_html()

        try:
            # Clear previous tool calls for new conversation
            self.current_tool_calls = []

            # Add user message to history with name
            user_message = f"**You:** {message}"
            history.append({"role": "user", "content": user_message})

            # Create message object
            messages = [Message(role="user", content=message)]

            # Map agent choice to agent name and display name (sync with bedrock app)
            agent_map = {
                "🎯 Data Manager (Coordinator)": ("data_manager", "Data Manager"),
                "📊 Data Analyst": ("data_analyst", "Data Analyst"),
                "⚙️ Data Engineer": ("data_engineer", "Data Engineer"),
                "👤 Tableau Admin": ("tableau_admin", "Tableau Admin"),
                "📋 Data Admin": ("data_admin", "Data Admin"),
            }

            selected_agent, agent_display_name = agent_map.get(
                agent_choice, ("data_manager", "Data Manager")
            )

            # Get the conversation logger to track tool calls
            conv_logger = get_conversation_logger()

            # Store reference to track tool calls for this conversation
            initial_conversation_count = conv_logger.conversation_count

            # Process the request
            result = await self.system.process_request(messages, agent=selected_agent)

            # Capture tool calls from the conversation logger
            if (
                hasattr(conv_logger, "current_log_entry")
                and conv_logger.current_log_entry
            ):
                self.current_tool_calls = conv_logger.current_log_entry.get(
                    "tools_called", []
                )

            # Add assistant response to history with agent name
            agent_message = f"**{agent_display_name}:** {result.content}"
            history.append({"role": "assistant", "content": agent_message})

            # Log the conversation
            logger.info(f"User: {message}")
            logger.info(f"Agent ({selected_agent}): {result.content[:100]}...")

            # Generate tool calls HTML
            tool_calls_html = self.get_current_tool_calls_html()

            return history, "", tool_calls_html

        except Exception as e:
            error_msg = f"**System Error:** {str(e)}"
            logger.error(f"Chat error: {error_msg}")
            history.append({"role": "assistant", "content": error_msg})
            tool_calls_html = self.get_current_tool_calls_html()
            return history, "", tool_calls_html

    def sync_chat(self, message: str, history: List[dict], agent_choice: str):
        """Synchronous wrapper for the async chat method."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self.chat(message, history, agent_choice))
        finally:
            loop.close()

    def create_interface(self):
        """Create the Gradio interface."""

        # Simplified CSS for better visibility
        custom_css = """
        .header-section {
            background: #000000;
            color: white;
            padding: 20px;
            text-align: center;
            margin-bottom: 10px;
        }
        .header-title {
            font-size: 28px;
            font-weight: 600;
            margin-bottom: 8px;
            color: white !important;
        }
        .header-subtitle {
            font-size: 14px;
            margin-bottom: 10px;
            color: white !important;
        }
        .powered-by {
            font-size: 12px;
            display: flex;
            justify-content: center;
            gap: 15px;
            flex-wrap: wrap;
            color: white !important;
        }
        .powered-by span {
            color: white !important;
        }
        .tool-panel {
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 6px;
            padding: 15px;
            max-height: 500px;
            overflow-y: auto;
        }
        .tool-call {
            background: white;
            border: 1px solid #dee2e6;
            border-radius: 6px;
            padding: 10px;
            margin-bottom: 10px;
            font-size: 12px;
        }
        .tool-name {
            font-weight: 600;
            color: #1e3a8a;
            margin-bottom: 5px;
        }
        .tool-args {
            color: #666;
            font-family: monospace;
        }
        """

        with gr.Blocks(
            css=custom_css, title="MECCA Data Team AI Assistant", theme=gr.themes.Soft()
        ) as interface:
            # Header with branding
            gr.HTML("""
            <div class="header-section">
                <div class="header-title">MECCA Data Team AI Hub (Prototype V25.08.23)</div>
                <div class="header-subtitle">Intelligent data operations powered by AWS Bedrock Claude 3.5 Sonnet</div>
                <div class="powered-by">
                    <span>🔗 AWS Bedrock</span>
                    <span>🚀 Lumos AI</span>
                    <span>🏗️ dbt Cloud</span>
                    <span>📊 Tableau REST API</span>
                    <span>🎯 Jira API</span>
                </div>
            </div>
            """)

            with gr.Row():
                with gr.Column(scale=6):
                    # Main chat interface
                    chatbot = gr.Chatbot(height=600, show_label=False, type="messages")

                    # Message input area (moved to bottom for better visibility)
                    msg = gr.Textbox(
                        placeholder="Ask about data, analytics, dbt models, Tableau users, or create Jira issues...",
                        lines=1,
                        max_lines=3,
                        show_label=False,
                        submit_btn=True,
                    )

                with gr.Column(scale=4):
                    # Tool thinking panel
                    gr.HTML(
                        '<h4 style="margin: 0 0 10px 0; color: #1e3a8a;">🔧 AI Thinking Process</h4>'
                    )
                    tool_panel = gr.HTML(
                        '<div class="tool-panel"><p style="color: #666; font-style: italic;">Tool calls will appear here during processing...</p></div>'
                    )

            # Event handlers
            def submit_message(message, history):
                if message.strip():
                    # Always use Data Manager (Coordinator) as default
                    selected_agent = "🎯 Data Manager (Coordinator)"
                    new_history, empty_msg, tool_html = self.sync_chat(
                        message, history, selected_agent
                    )
                    return new_history, empty_msg, tool_html
                return history, message, self.get_current_tool_calls_html()

            # Bind events
            msg.submit(
                submit_message,
                inputs=[msg, chatbot],
                outputs=[chatbot, msg, tool_panel],
            )

        return interface

    def get_current_tool_calls_html(self):
        """Generate HTML for current conversation's tool calls."""
        if not self.current_tool_calls:
            return """
            <div class="tool-panel">
                <p style="color: #666; font-style: italic; text-align: center; padding: 20px;">
                    🤖 AI thinking process will appear here during processing...
                </p>
            </div>
            """

        html_parts = ['<div class="tool-panel">']

        # Add thinking process header
        html_parts.append(f"""
            <div style="margin-bottom: 15px; padding: 10px; background: #e3f2fd; border-radius: 6px; border-left: 4px solid #1976d2;">
                <strong>🧠 AI Thinking Process</strong><br>
                <small style="color: #666;">{len(self.current_tool_calls)} tools executed</small>
            </div>
        """)

        # Add each tool call
        for i, tool_call in enumerate(self.current_tool_calls, 1):
            tool_name = tool_call.get("tool_name", "Unknown Tool")
            tool_input = tool_call.get("tool_input", {})
            tool_result = tool_call.get("tool_result", {})
            timestamp = tool_call.get("timestamp", "")

            # Format timestamp
            try:
                if timestamp:
                    from datetime import datetime

                    dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                    time_str = dt.strftime("%H:%M:%S")
                else:
                    time_str = ""
            except:
                time_str = ""

            # Determine status icon and color
            success = tool_result.get("success", False)
            status_icon = "✅" if success else "❌"
            border_color = "#4caf50" if success else "#f44336"

            # Format tool input parameters
            input_parts = []
            for key, value in tool_input.items():
                if isinstance(value, str) and len(value) > 50:
                    value = value[:47] + "..."
                input_parts.append(f"{key}={value}")
            input_str = ", ".join(input_parts) if input_parts else "No parameters"

            # Get tool result summary
            if success:
                result_data = tool_result.get("result")
                if isinstance(result_data, dict):
                    if "total_users" in result_data:
                        result_summary = f"Found {result_data['total_users']} users"
                    elif "total_workbooks" in result_data:
                        result_summary = (
                            f"Found {result_data['total_workbooks']} workbooks"
                        )
                    elif "total_datasources" in result_data:
                        result_summary = (
                            f"Found {result_data['total_datasources']} datasources"
                        )
                    elif "models" in result_data:
                        result_summary = (
                            f"Found {len(result_data.get('models', []))} models"
                        )
                    else:
                        result_summary = "Success"
                else:
                    result_summary = "Success"
            else:
                error = tool_result.get("error", "Unknown error")
                result_summary = (
                    f"Error: {error[:50]}..." if len(error) > 50 else f"Error: {error}"
                )

            html_parts.append(f"""
                <div class="tool-call" style="border-left: 3px solid {border_color};">
                    <div style="display: flex; justify-content: between; align-items: center; margin-bottom: 5px;">
                        <div class="tool-name" style="flex: 1;">
                            <span style="font-size: 14px;">{status_icon} <strong>{tool_name}</strong></span>
                            {f'<small style="color: #666; margin-left: 10px;">{time_str}</small>' if time_str else ""}
                        </div>
                    </div>
                    <div class="tool-args" style="color: #666; font-size: 11px; margin-bottom: 8px;">
                        📝 <strong>Input:</strong> {input_str}
                    </div>
                    <div style="color: #333; font-size: 11px; padding: 5px 0;">
                        📊 <strong>Result:</strong> {result_summary}
                    </div>
                </div>
            """)

        html_parts.append("</div>")
        return "".join(html_parts)

    def launch(self, **kwargs):
        """Launch the Gradio interface."""
        interface = self.create_interface()

        # Default launch parameters
        launch_params = {
            "server_name": "0.0.0.0",
            "server_port": 7860,
            "share": False,
            "debug": False,
            "show_error": True,
            "quiet": False,
        }

        # Override with any provided parameters
        launch_params.update(kwargs)

        logger.info(
            f"Starting Gradio interface on {launch_params['server_name']}:{launch_params['server_port']}"
        )

        return interface.launch(**launch_params)


def main():
    """Main entry point for the Gradio app."""
    app = GradioBedrockApp()
    app.launch()


if __name__ == "__main__":
    main()
