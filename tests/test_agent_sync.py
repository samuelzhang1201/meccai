#!/usr/bin/env python3
"""
Test script to verify all agents work consistently between Bedrock and Gradio apps.
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from meccaai.apps.gradio_app import GradioBedrockApp
from meccaai.apps.lumos_bedrock_agents import LumosBedrockAgentSystem
from meccaai.core.types import Message


async def test_agent_consistency():
    """Test that all agents work consistently in both apps."""
    print("=" * 100)
    print("🧪 TESTING AGENT CONSISTENCY BETWEEN BEDROCK AND GRADIO APPS")
    print("=" * 100)
    
    # Initialize both systems
    print("\n🔧 Initializing systems...")
    bedrock_system = LumosBedrockAgentSystem()
    gradio_app = GradioBedrockApp()
    
    # Test questions for each agent
    test_cases = [
        {
            "agent": "data_manager",
            "display_name": "🎯 Data Manager (Coordinator)",
            "question": "What services do you provide?",
            "expected_tools": ["self_intro_tool"]
        },
        {
            "agent": "data_analyst", 
            "display_name": "📊 Data Analyst",
            "question": "What metrics are available in our semantic layer?",
            "expected_tools": ["list_metrics"]
        },
        {
            "agent": "data_engineer",
            "display_name": "⚙️ Data Engineer", 
            "question": "Show me all dbt models in the project",
            "expected_tools": ["get_all_models"]
        },
        {
            "agent": "tableau_admin",
            "display_name": "👤 Tableau Admin",
            "question": "List all users on the Tableau site", 
            "expected_tools": ["get_users_on_site"]
        },
        {
            "agent": "data_admin",
            "display_name": "📋 Data Admin",
            "question": "Search for recent Jira issues",
            "expected_tools": ["search_issues"]
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        agent_name = test_case["agent"]
        display_name = test_case["display_name"]
        question = test_case["question"]
        
        print(f"\n{'='*60}")
        print(f"TEST {i}/5: {display_name}")
        print(f"Agent: {agent_name}")
        print(f"Question: {question}")
        print(f"{'='*60}")
        
        # Test Bedrock system
        print(f"\n🔹 Testing Bedrock System...")
        try:
            messages = [Message(role="user", content=question)]
            bedrock_result = await bedrock_system.process_request(messages, agent=agent_name)
            bedrock_success = True
            bedrock_response_length = len(bedrock_result.content)
            print(f"   ✅ Bedrock: Response received ({bedrock_response_length} characters)")
        except Exception as e:
            bedrock_success = False
            bedrock_response_length = 0
            print(f"   ❌ Bedrock: Failed - {str(e)[:100]}...")
        
        # Test Gradio system
        print(f"🔹 Testing Gradio System...")
        try:
            history = []
            gradio_history, _, tool_calls_html = await gradio_app.chat(
                question, history, display_name
            )
            gradio_success = True
            gradio_response_length = len(gradio_history[-1]['content']) if gradio_history else 0
            gradio_tools_count = len(gradio_app.current_tool_calls)
            print(f"   ✅ Gradio: Response received ({gradio_response_length} characters, {gradio_tools_count} tools called)")
        except Exception as e:
            gradio_success = False
            gradio_response_length = 0
            gradio_tools_count = 0
            print(f"   ❌ Gradio: Failed - {str(e)[:100]}...")
        
        # Record results
        test_result = {
            "agent": agent_name,
            "display_name": display_name,
            "bedrock_success": bedrock_success,
            "gradio_success": gradio_success,
            "consistent": bedrock_success == gradio_success,
            "bedrock_response_length": bedrock_response_length,
            "gradio_response_length": gradio_response_length,
            "gradio_tools_count": gradio_tools_count
        }
        results.append(test_result)
        
        # Show comparison
        if bedrock_success and gradio_success:
            print(f"   📊 Comparison: Both systems working ✅")
        elif bedrock_success and not gradio_success:
            print(f"   ⚠️  Comparison: Bedrock works, Gradio fails")
        elif not bedrock_success and gradio_success:
            print(f"   ⚠️  Comparison: Gradio works, Bedrock fails") 
        else:
            print(f"   ❌ Comparison: Both systems failed")
    
    # Summary report
    print(f"\n{'='*100}")
    print("📋 AGENT CONSISTENCY SUMMARY REPORT")
    print(f"{'='*100}")
    
    consistent_agents = sum(1 for r in results if r["consistent"])
    working_agents = sum(1 for r in results if r["bedrock_success"] and r["gradio_success"])
    
    print(f"\n📊 OVERALL STATISTICS:")
    print(f"   • Total agents tested: {len(results)}")
    print(f"   • Agents working in both systems: {working_agents}/{len(results)}")
    print(f"   • Agents with consistent behavior: {consistent_agents}/{len(results)}")
    print(f"   • Success rate: {(working_agents/len(results)*100):.1f}%")
    
    print(f"\n📋 DETAILED RESULTS:")
    print(f"{'AGENT':<20} {'BEDROCK':<10} {'GRADIO':<10} {'CONSISTENT':<12} {'TOOLS':<8}")
    print("-" * 70)
    
    for result in results:
        agent_name = result["display_name"][:18]
        bedrock_status = "✅ Yes" if result["bedrock_success"] else "❌ No"
        gradio_status = "✅ Yes" if result["gradio_success"] else "❌ No" 
        consistent_status = "✅ Yes" if result["consistent"] else "❌ No"
        tools_count = result["gradio_tools_count"]
        
        print(f"{agent_name:<20} {bedrock_status:<10} {gradio_status:<10} {consistent_status:<12} {tools_count:<8}")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    failing_agents = [r for r in results if not (r["bedrock_success"] and r["gradio_success"])]
    if failing_agents:
        print("   • Fix failing agents:")
        for agent in failing_agents:
            print(f"     - {agent['display_name']}: {'Bedrock failed' if not agent['bedrock_success'] else ''} {'Gradio failed' if not agent['gradio_success'] else ''}")
    else:
        print("   ✅ All agents working consistently! System is synchronized.")
    
    print(f"\n{'='*100}")
    if working_agents == len(results):
        print("🎉 SUCCESS: All agents work consistently in both systems!")
    else:
        print(f"⚠️  PARTIAL SUCCESS: {working_agents}/{len(results)} agents working consistently")
    print(f"{'='*100}")
    
    return results


async def main():
    """Run the consistency test."""
    print("🚀 Starting Agent Consistency Test...")
    print("This will test all 5 agents in both Bedrock and Gradio systems")
    print("to ensure they behave the same way and have the same functions.")
    
    results = await test_agent_consistency()
    return results


if __name__ == "__main__":
    asyncio.run(main())