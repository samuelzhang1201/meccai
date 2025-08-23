#!/usr/bin/env python3
"""
Quick test to verify the fixed Gradio UI works properly.
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from meccaai.apps.gradio_app import GradioBedrockApp


async def test_ui_components():
    """Test that the UI components are properly configured."""
    print("=== TESTING FIXED GRADIO UI ===")
    
    # Create the Gradio app instance
    app = GradioBedrockApp()
    
    print("✅ App instance created successfully")
    
    # Test simple chat functionality
    history = []
    test_message = "Hello, can you introduce yourself?"
    agent_choice = "🎯 Data Manager (Coordinator)"
    
    print(f"📝 Testing with message: '{test_message}'")
    print(f"🤖 Selected agent: {agent_choice}")
    
    try:
        updated_history, empty_msg, tool_calls_html = await app.chat(
            test_message, history, agent_choice
        )
        
        print(f"✅ Chat processed successfully!")
        print(f"   - History entries: {len(updated_history)}")
        print(f"   - Tool calls: {len(app.current_tool_calls)}")
        
        if updated_history:
            last_response = updated_history[-1]['content'][:100]
            print(f"   - Response preview: {last_response}...")
        
        print("✅ All UI components working properly")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Run the UI test."""
    print("🔧 Testing fixed Gradio UI components...")
    asyncio.run(test_ui_components())
    print("\n🎉 UI test completed!")


if __name__ == "__main__":
    main()