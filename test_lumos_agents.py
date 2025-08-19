#!/usr/bin/env python3
"""Test script for Lumos Agents with dbt and Tableau tools."""

import asyncio
import os
from dotenv import load_dotenv
from agents import Runner

# Load environment variables from .env file
load_dotenv()

from meccaai.apps.lumos_agents import get_agents


async def test_lumos_agents():
    """Test the Lumos agents with 3 questions using dbt and Tableau tools."""
    
    # Get the agents
    agents = get_agents()
    data_analyst = agents["data_analyst"]
    
    # Test questions
    questions = [
        # Question 1: DBT related
        "Can you help me list all the dbt models in our project and then compile the dbt project? I want to understand what data models we have available.",
        
        # Question 2: Tableau related  
        "I need to see what Tableau views are available and get information about a specific view. Can you help me list the views and show me details about one of them?",
        
        # Question 3: Mixed - dbt and Tableau workflow
        "I want to run a complete data pipeline: first run the dbt models to update our data, then check what Tableau dashboards we have that might need to be refreshed. Can you help coordinate this workflow?"
    ]
    
    print("🤖 Testing Lumos Data Analyst Agent")
    print("=" * 60)
    
    for i, question in enumerate(questions, 1):
        print(f"\n📝 Question {i}:")
        print(f"User: {question}")
        print("\n🔄 Processing...")
        
        try:
            # Run the agent with the question  
            result = await Runner().run(data_analyst, question)
            
            print(f"\n🤖 Data Analyst Response:")
            print("-" * 40)
            if hasattr(result, 'final_output'):
                print(result.final_output)
            else:
                print(str(result))
            
            print("\n" + "=" * 60)
            
        except Exception as e:
            print(f"\n❌ Error processing question {i}: {str(e)}")
            print(f"Error type: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            print("=" * 60)
    
    # Test agent capabilities
    print(f"\n📊 Agent Capabilities Summary:")
    print(f"Tools available: {len(data_analyst.tools)}")
    print(f"Handoffs available: {len(data_analyst.handoffs)}")
    print(f"Output guardrails: {len(data_analyst.output_guardrails)}")
    
    # List available tools
    print(f"\n🔧 Available Tools:")
    for i, tool in enumerate(data_analyst.tools, 1):
        tool_name = getattr(tool, 'name', f'Tool_{i}')
        print(f"  {i}. {tool_name}")


def test_agent_import():
    """Test basic agent import and setup."""
    print("🧪 Testing Lumos Agents Import...")
    
    try:
        from meccaai.apps.lumos_agents import get_agents, get_tool_agents
        
        agents = get_agents()
        tool_agents = get_tool_agents()
        
        print("✅ Import successful!")
        print(f"Main agents: {list(agents.keys())}")
        print(f"Tool agents: {list(tool_agents.keys())}")
        
        # Test data analyst
        data_analyst = agents["data_analyst"]
        print(f"Data Analyst tools: {len(data_analyst.tools)}")
        print(f"Data Analyst handoffs: {len(data_analyst.handoffs)}")
        print(f"Data Analyst guardrails: {len(data_analyst.output_guardrails)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🚀 Starting Lumos Agents Test")
    print("=" * 60)
    
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY environment variable not set")
        print("The agents may not work properly without an API key")
    
    # Test import first
    if test_agent_import():
        print("\n" + "=" * 60)
        
        # Run the main test
        try:
            asyncio.run(test_lumos_agents())
        except Exception as e:
            print(f"❌ Test failed: {str(e)}")
            import traceback
            traceback.print_exc()
    else:
        print("❌ Skipping main test due to import failure")
    
    print("\n🏁 Test completed!")