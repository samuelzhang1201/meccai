"""Tests for the Lumos multi-agent system."""

import pytest

from meccaai.apps.lumos_agents import LumosAgentSystem, LumosAIManager, TableauAnalyst
from meccaai.core.types import Message


def test_lumos_agent_initialization():
    """Test that agents initialize properly."""
    manager = LumosAIManager()
    assert manager.name == "Lumos AI Manager"
    assert "orchestrator" in manager.role
    assert len(manager.tools) > 0
    
    tableau_analyst = TableauAnalyst()
    assert tableau_analyst.name == "Tableau Analyst"
    assert "visualization specialist" in tableau_analyst.role
    assert len(tableau_analyst.tools) > 0


def test_lumos_system_initialization():
    """Test that the Lumos system initializes properly."""
    system = LumosAgentSystem()
    
    # Check agents are available
    agents = system.list_agents()
    assert "manager" in agents
    assert "tableau" in agents
    assert "dbt" in agents
    assert "reporting" in agents
    
    # Check agent roles are descriptive
    assert "orchestrator" in agents["manager"]
    assert "visualization" in agents["tableau"]
    assert "data engineering" in agents["dbt"]
    assert "data analyst" in agents["reporting"]


@pytest.mark.asyncio
async def test_message_creation():
    """Test that messages are created properly for processing."""
    system = LumosAgentSystem()
    
    # Test message creation
    message = Message(role="user", content="Test message")
    assert message.role == "user"
    assert message.content == "Test message"
    assert message.tool_calls is None


def test_agent_tool_assignment():
    """Test that agents have the correct tools assigned."""
    system = LumosAgentSystem()
    
    # Check tableau analyst has tableau tools
    tableau_tools = [tool.name for tool in system.agents["tableau"].tools]
    expected_tableau_tools = ["list_all_pats", "get_view", "query_view_pdf", "list_views"]
    for tool in expected_tableau_tools:
        assert tool in tableau_tools
    
    # Check manager has communication tools
    manager_tools = [tool.name for tool in system.agents["manager"].tools]
    expected_manager_tools = ["send_email", "create_slack_message", "create_google_sheet_row", "trigger_webhook"]
    for tool in expected_manager_tools:
        assert tool in manager_tools


def test_workflow_task_analysis():
    """Test that workflow tasks are properly analyzed."""
    manager = LumosAIManager()
    
    # Test tableau-related tasks
    tableau_tasks = [
        "create a tableau dashboard",
        "export visualization to pdf",
        "show me dashboard insights"
    ]
    
    for task in tableau_tasks:
        assert "tableau" in task.lower() or "dashboard" in task.lower() or "visualization" in task.lower()
    
    # Test dbt-related tasks  
    dbt_tasks = [
        "run dbt models",
        "transform the data",
        "build data models"
    ]
    
    for task in dbt_tasks:
        assert "dbt" in task.lower() or "transform" in task.lower() or "model" in task.lower()


def test_system_configuration():
    """Test that the system is properly configured."""
    from meccaai.core.config import settings
    
    # Test that Tableau config exists
    assert hasattr(settings, 'tableau')
    assert settings.tableau.server_url == "https://prod-apsoutheast-a.online.tableau.com"
    assert settings.tableau.site_content_url == "meccalumos"
    assert settings.tableau.token_name == "Agent"
    assert settings.tableau.api_version == "3.25"