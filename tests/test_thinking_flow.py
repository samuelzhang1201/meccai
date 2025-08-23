#!/usr/bin/env python3
"""
Test script to demonstrate the thinking flow capture with tableau and dbt tools.
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from meccaai.apps.gradio_app import GradioBedrockApp


async def test_thinking_flow():
    """Test the thinking flow display with actual tool calls."""
    print("=" * 80)
    print("🧪 TESTING GRADIO UI THINKING FLOW")
    print("=" * 80)
    
    # Create the Gradio app instance
    app = GradioBedrockApp()
    
    # Test message that should trigger both tableau and dbt tools
    test_message = "Show me the tableau users and dbt model execution times"
    
    print(f"\n📝 Testing with message: '{test_message}'")
    print("-" * 60)
    
    # Initialize empty history
    history = []
    agent_choice = "Data Manager (Coordinator)"
    
    try:
        # Call the chat method directly
        print("🤖 Processing request...")
        updated_history, empty_msg, tool_calls_html = await app.chat(
            test_message, history, agent_choice
        )
        
        # Display results
        print(f"\n📊 RESULTS:")
        print(f"History entries: {len(updated_history)}")
        print(f"Tool calls captured: {len(app.current_tool_calls)}")
        
        if app.current_tool_calls:
            print(f"\n🔧 TOOLS CALLED:")
            for i, tool_call in enumerate(app.current_tool_calls, 1):
                tool_name = tool_call.get('tool_name', 'Unknown')
                success = tool_call.get('tool_result', {}).get('success', False)
                status = "✅ Success" if success else "❌ Failed"
                print(f"  {i}. {tool_name} - {status}")
        
        print(f"\n🌐 HTML OUTPUT FOR UI:")
        print(tool_calls_html)
        
        # Show conversation history
        print(f"\n💬 CONVERSATION HISTORY:")
        for i, entry in enumerate(updated_history, 1):
            role = entry.get('role', 'unknown')
            content = entry.get('content', '')[:100]
            print(f"  {i}. [{role.upper()}]: {content}...")
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\n{'=' * 80}")
    print("✅ THINKING FLOW TEST COMPLETED")
    print(f"{'=' * 80}")


def main():
    """Run the test."""
    print("Starting thinking flow test...")
    print("This will test if the UI properly captures and displays tool calls.")
    
    asyncio.run(test_thinking_flow())


if __name__ == "__main__":
    main()