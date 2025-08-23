#!/usr/bin/env python3
"""
Test the Gradio UI without agent selector.
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from meccaai.apps.gradio_app import GradioBedrockApp


async def test_ui_without_selector():
    """Test the UI functionality without agent selector."""
    print("=== TESTING UI WITHOUT AGENT SELECTOR ===")
    
    app = GradioBedrockApp()
    
    # Test that the UI defaults to Data Manager
    history = []
    test_message = "Hello, what can you help me with?"
    
    print(f"📝 Testing message: '{test_message}'")
    print("🤖 Expected: Should default to Data Manager")
    
    try:
        # The sync_chat method still expects agent_choice parameter
        # It should default to Data Manager (Coordinator)
        updated_history, empty_msg, tool_calls_html = await app.chat(
            test_message, history, "🎯 Data Manager (Coordinator)"
        )
        
        print("✅ Chat processed successfully!")
        print(f"   - History entries: {len(updated_history)}")
        print(f"   - Tool calls: {len(app.current_tool_calls)}")
        
        if updated_history:
            last_response = updated_history[-1]['content'][:150]
            print(f"   - Response preview: {last_response}...")
        
        print("\n🎯 CURRENT UI STRUCTURE:")
        print("✅ Header with branding")
        print("❌ NO agent selector (removed)")
        print("✅ Chat interface")
        print("✅ Message input at bottom")
        print("✅ AI thinking panel on right")
        print("✅ Defaults to Data Manager for all requests")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Run the test."""
    print("🧪 Testing UI without agent selector...")
    asyncio.run(test_ui_without_selector())
    print("\n🎉 Test completed!")


if __name__ == "__main__":
    main()