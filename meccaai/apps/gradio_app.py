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
        history: List[Tuple[str, str]], 
        agent_choice: str
    ) -> Tuple[List[Tuple[str, str]], str]:
        """Process a chat message and return updated history."""
        if not message.strip():
            return history, ""

        try:
            # Add user message to history
            history.append((message, ""))
            
            # Create message object
            messages = [Message(role="user", content=message)]
            
            # Map agent choice to agent name
            agent_map = {
                "Data Manager (Coordinator)": "data_manager",
                "Data Analyst": "data_analyst", 
                "Data Engineer": "data_engineer",
                "Tableau Admin": "tableau_admin",
                "Data Admin": "data_admin"
            }
            
            selected_agent = agent_map.get(agent_choice, "data_manager")
            
            # Process the request
            result = await self.system.process_request(
                messages, agent=selected_agent
            )
            
            # Update the last message in history with the response
            history[-1] = (message, result.content)
            
            # Log the conversation
            logger.info(f"User: {message}")
            logger.info(f"Agent ({selected_agent}): {result.content[:100]}...")
            
            return history, ""
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            logger.error(f"Chat error: {error_msg}")
            history[-1] = (message, error_msg)
            return history, ""

    def sync_chat(self, message: str, history: List[Tuple[str, str]], agent_choice: str):
        """Synchronous wrapper for the async chat method."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self.chat(message, history, agent_choice))
        finally:
            loop.close()

    def create_interface(self):
        """Create the Gradio interface."""
        
        # Custom CSS for better styling
        custom_css = """
        .gradio-container {
            max-width: 1200px !important;
            margin: auto;
        }
        .main-header {
            text-align: center;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .agent-info {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            margin: 10px 0;
            border-left: 4px solid #007bff;
        }
        """
        
        with gr.Blocks(
            css=custom_css,
            title="Lumos AI - Data Intelligence Assistant",
            theme=gr.themes.Soft()
        ) as interface:
            
            # Header
            gr.HTML("""
            <div class="main-header">
                <h1>🤖 Lumos AI - Data Intelligence Assistant</h1>
                <p>Powered by AWS Bedrock | Multi-Agent System for Data Operations</p>
            </div>
            """)
            
            with gr.Row():
                with gr.Column(scale=3):
                    # Chat interface
                    chatbot = gr.Chatbot(
                        label="💬 Conversation",
                        height=500,
                        show_label=True,
                        bubble_full_width=False,
                    )
                    
                    msg = gr.Textbox(
                        label="Your Message",
                        placeholder="Ask me about data, analytics, Tableau users, or anything else... (Press Enter to send, Shift+Enter for new line)",
                        lines=3,
                        max_lines=10,
                        submit_btn=True
                    )
                    
                    # Example queries
                    gr.Examples(
                        examples=[
                            "Show me all Tableau users",
                            "List all dbt models in the mart layer",
                            "What metrics are available in our semantic layer?",
                            "Create a Jira issue for data quality improvements",
                            "Export user data to CSV",
                            "Run dbt tests for the marketing models"
                        ],
                        inputs=msg,
                        label="💡 Example Queries"
                    )
                    
                with gr.Column(scale=1):
                    # Agent selection
                    agent_choice = gr.Dropdown(
                        choices=[
                            "Data Manager (Coordinator)",
                            "Data Analyst", 
                            "Data Engineer",
                            "Tableau Admin",
                            "Data Admin"
                        ],
                        value="Data Manager (Coordinator)",
                        label="🎯 Select Agent",
                        info="Choose which specialist to talk to"
                    )
                    
                    # Agent information
                    gr.HTML("""
                    <div class="agent-info">
                        <h3>🧠 Agent Roles:</h3>
                        <ul>
                            <li><strong>Data Manager:</strong> Coordinates all agents and handles complex workflows</li>
                            <li><strong>Data Analyst:</strong> Semantic layer queries and data insights</li>
                            <li><strong>Data Engineer:</strong> dbt projects and data pipelines</li>
                            <li><strong>Tableau Admin:</strong> User management and site administration</li>
                            <li><strong>Data Admin:</strong> Jira project management and issue tracking</li>
                        </ul>
                    </div>
                    """)
                    
                    # Clear conversation
                    clear_btn = gr.Button("🗑️ Clear Conversation", variant="secondary")
                    
                    # System status
                    gr.HTML("""
                    <div class="agent-info">
                        <h3>📊 System Status:</h3>
                        <p>✅ AWS Bedrock Connected<br>
                        ✅ All Agents Online<br>
                        ✅ Tools Available</p>
                    </div>
                    """)
            
            # Event handlers
            def submit_message(message, history, agent):
                if message.strip():
                    return self.sync_chat(message, history, agent)
                return history, message
            
            def clear_conversation():
                return [], ""
            
            # Bind events
            msg.submit(
                submit_message,
                inputs=[msg, chatbot, agent_choice],
                outputs=[chatbot, msg]
            )
            
            clear_btn.click(
                clear_conversation,
                outputs=[chatbot, msg]
            )
        
        return interface

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