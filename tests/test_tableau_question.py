#!/usr/bin/env python3
"""
Test the Gradio UI with a Tableau-focused question to show thinking flow.
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from meccaai.apps.gradio_app import GradioBedrockApp


async def test_tableau_question():
    """Test with a Tableau-focused question."""
    print("=" * 80)
    print("🧪 TESTING GRADIO UI WITH TABLEAU QUESTION")
    print("=" * 80)
    
    # Create the Gradio app instance
    app = GradioBedrockApp()
    
    # Test message focused on Tableau
    test_message = "List all tableau users on the site and show me their roles"
    
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
                
                # Get some result details
                tool_result = tool_call.get('tool_result', {})
                if success and tool_result.get('result'):
                    result_data = tool_result.get('result')
                    if isinstance(result_data, dict) and 'total_users' in result_data:
                        details = f"(Found {result_data['total_users']} users)"
                    else:
                        details = ""
                else:
                    details = ""
                    
                print(f"  {i}. {tool_name} - {status} {details}")
        
        print(f"\n🌐 HTML OUTPUT FOR UI (first 500 chars):")
        print(tool_calls_html[:500] + "..." if len(tool_calls_html) > 500 else tool_calls_html)
        
        # Show conversation history
        print(f"\n💬 CONVERSATION SUMMARY:")
        for i, entry in enumerate(updated_history, 1):
            role = entry.get('role', 'unknown')
            content = entry.get('content', '')
            content_preview = content[:150] + "..." if len(content) > 150 else content
            print(f"  {i}. [{role.upper()}]: {content_preview}")
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\n{'=' * 80}")
    print("✅ TABLEAU THINKING FLOW TEST COMPLETED")
    print(f"{'=' * 80}")


def main():
    """Run the test."""
    print("🚀 Starting Tableau-focused thinking flow test...")
    print("This will test Tableau user listing with thinking process display.")
    
    asyncio.run(test_tableau_question())


if __name__ == "__main__":
    main()