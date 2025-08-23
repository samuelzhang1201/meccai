"""Gradio web interface for Lumos AI Bedrock Agent System."""

import asyncio
import json
from datetime import datetime
from typing import List, Tuple

import gradio as gr

from meccaai.apps.lumos_bedrock_agents import LumosBedrockAgentSystem
from meccaai.core.logging import get_logger
from meccaai.core.types import Message

logger = get_logger(__name__)


class GradioBedrockApp:
    """Gradio web interface for the Bedrock agent system."""

    def __init__(self):
        """Initialize the Gradio app."""
        self.system = LumosBedrockAgentSystem()
        self.conversation_history = []

    async def chat(
        self, 
        message: str, 
        history: List[dict], 
        agent_choice: str
    ) -> Tuple[List[dict], str]:
        """Process a chat message and return updated history."""
        if not message.strip():
            return history, ""

        try:
            # Add user message to history with name
            user_message = f"**You:** {message}"
            history.append({"role": "user", "content": user_message})
            
            # Create message object
            messages = [Message(role="user", content=message)]
            
            # Map agent choice to agent name and display name
            agent_map = {
                "Data Manager (Coordinator)": ("data_manager", "Data Manager"),
                "Data Analyst": ("data_analyst", "Data Analyst"), 
                "Data Engineer": ("data_engineer", "Data Engineer"),
                "Tableau Admin": ("tableau_admin", "Tableau Admin"),
                "Data Admin": ("data_admin", "Data Admin")
            }
            
            selected_agent, agent_display_name = agent_map.get(agent_choice, ("data_manager", "Data Manager"))
            
            # Process the request
            result = await self.system.process_request(
                messages, agent=selected_agent
            )
            
            # Add assistant response to history with agent name
            agent_message = f"**{agent_display_name}:** {result.content}"
            history.append({"role": "assistant", "content": agent_message})
            
            # Log the conversation
            logger.info(f"User: {message}")
            logger.info(f"Agent ({selected_agent}): {result.content[:100]}...")
            
            return history, ""
            
        except Exception as e:
            error_msg = f"**System Error:** {str(e)}"
            logger.error(f"Chat error: {error_msg}")
            history.append({"role": "assistant", "content": error_msg})
            return history, ""

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
        
        # Custom CSS for responsive full-screen layout
        custom_css = """
        .gradio-container {
            height: 100vh !important;
            max-width: none !important;
            margin: 0 !important;
            padding: 0 !important;
        }
        .header-section {
            background: #000000;
            color: white;
            padding: 20px;
            text-align: center;
            margin-bottom: 0;
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
        /* Force initial layout proportions */
        .main-row {
            display: flex !important;
            height: calc(100vh - 180px) !important;
        }
        .chat-column {
            width: 60% !important;
            min-width: 60% !important;
            flex: 0 0 60% !important;
            display: flex !important;
            flex-direction: column !important;
        }
        .thinking-column {
            width: 40% !important;
            min-width: 40% !important;
            flex: 0 0 40% !important;
        }
        .tool-panel {
            background: #f8f9fa;
            border-left: 2px solid #e9ecef;
            height: calc(100vh - 180px);
            overflow-y: auto;
            padding: 15px;
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
        .chat-area {
            flex: 1 !important;
            display: flex !important;
            flex-direction: column !important;
            min-height: 0 !important;
        }
        .input-area {
            padding: 10px 0;
            border-top: 1px solid #e9ecef;
            flex-shrink: 0 !important;
        }
        
        /* Responsive design */
        @media (max-width: 1200px) {
            .header-title { font-size: 24px; }
            .powered-by { gap: 10px; }
        }
        @media (max-width: 768px) {
            .header-title { font-size: 20px; }
            .header-subtitle { font-size: 12px; }
            .powered-by { font-size: 10px; gap: 8px; }
            .chat-column { width: 100% !important; flex: 0 0 100% !important; }
            .thinking-column { display: none !important; }
        }
        @media (min-width: 1920px) {
            .header-title { font-size: 32px; }
            .header-subtitle { font-size: 16px; }
        }
        """
        
        with gr.Blocks(
            css=custom_css,
            title="MECCA Data Team AI Assistant",
            theme=gr.themes.Soft(),
            fill_height=True
        ) as interface:
            
            # Header with branding
            gr.HTML("""
            <div class="header-section">
                <div class="header-title">MECCA Data Team AI Assistant (Prototype)</div>
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
            
            with gr.Row(elem_classes=["main-row"]):
                with gr.Column(scale=6, elem_classes=["chat-column"]):
                    with gr.Column(elem_classes=["chat-area"]):
                        # Main chat interface
                        chatbot = gr.Chatbot(
                            height="calc(100vh - 250px)",
                            show_label=False,
                            container=False,
                            bubble_full_width=False,
                            type="messages"
                        )
                        
                        # Message input area
                        with gr.Row(elem_classes=["input-area"]):
                            msg = gr.Textbox(
                                placeholder="Ask about data, analytics, dbt models, Tableau users, or create Jira issues...",
                                lines=1,
                                max_lines=5,
                                show_label=False,
                                container=False,
                                submit_btn=True,
                                scale=10
                            )
                
                with gr.Column(scale=4, elem_classes=["thinking-column"]):
                    # Tool thinking panel
                    gr.HTML('<h4 style="margin: 0 0 10px 0; color: #1e3a8a;">🔧 AI Thinking Process</h4>')
                    tool_panel = gr.HTML(
                        '<div class="tool-panel"><p style="color: #666; font-style: italic;">Tool calls will appear here during processing...</p></div>',
                        elem_classes=["tool-panel"]
                    )
            
            # Hidden agent selection (defaults to data manager)  
            agent_choice = gr.State(value="Data Manager (Coordinator)")
            
            # Event handlers
            def submit_message(message, history):
                if message.strip():
                    new_history, empty_msg = self.sync_chat(message, history, "Data Manager (Coordinator)")
                    # Update tool panel with recent activity
                    tool_html = self.get_recent_tool_calls()
                    return new_history, empty_msg, tool_html
                return history, message, tool_panel.value
            
            # Bind events
            msg.submit(
                submit_message,
                inputs=[msg, chatbot],
                outputs=[chatbot, msg, tool_panel]
            )
        
        return interface
    
    def get_recent_tool_calls(self):
        """Generate HTML for recent tool calls (placeholder for now)."""
        return """
        <div class="tool-panel">
            <div class="tool-call">
                <div class="tool-name">🤖 agent_coordinator</div>
                <div class="tool-args">Analyzing user request...</div>
            </div>
            <div class="tool-call">
                <div class="tool-name">🔍 data_analyst_agent</div>
                <div class="tool-args">Processing data query...</div>
            </div>
            <div class="tool-call">
                <div class="tool-name">📊 get_tableau_users</div>
                <div class="tool-args">limit=50, active_only=true</div>
            </div>
            <div class="tool-call">
                <div class="tool-name">✅ export_to_csv</div>
                <div class="tool-args">filename="users_export.csv"</div>
            </div>
        </div>
        """

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
        
        logger.info(f"Starting Gradio interface on {launch_params['server_name']}:{launch_params['server_port']}")
        
        return interface.launch(**launch_params)


def main():
    """Main entry point for the Gradio app."""
    app = GradioBedrockApp()
    app.launch()


if __name__ == "__main__":
    main()