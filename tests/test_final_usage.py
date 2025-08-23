#!/usr/bin/env python3
"""
Final test of the usage workflow with the exact user question.
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from meccaai.apps.gradio_app import GradioBedrockApp


async def test_final_usage():
    """Test the exact user question."""
    print("=== FINAL USAGE TEST ===")
    
    app = GradioBedrockApp()
    
    # The exact question from the user
    question = "show me the workbook content with times viewed by users less than 20 times, show me workbook name, owner, viewed times"
    
    print(f"📝 User question: '{question}'")
    
    history = []
    
    try:
        # Set a shorter timeout and monitor the response
        print("🤖 Processing request (this may take a moment)...")
        
        updated_history, empty_msg, tool_calls_html = await app.chat(
            question, history, "🎯 Data Manager (Coordinator)"
        )
        
        print(f"\n✅ Got response!")
        print(f"   - Tool calls: {len(app.current_tool_calls)}")
        
        # Check if usage API was called with content items
        usage_called_properly = False
        for tool_call in app.current_tool_calls:
            tool_name = tool_call.get('tool_name')
            if tool_name == 'get_content_usage':
                tool_input = tool_call.get('tool_input', {})
                content_items = tool_input.get('content_items', [])
                success = tool_call.get('tool_result', {}).get('success', False)
                
                print(f"   - get_content_usage called with {len(content_items)} items")
                if len(content_items) > 0 and success:
                    usage_called_properly = True
                    print("   - ✅ Usage API called properly with workbook IDs")
        
        # Show the response
        if updated_history and len(updated_history) > 1:
            response = updated_history[-1]['content']
            
            if "hitsTotal" in response or "viewed" in response or "views" in response:
                print(f"\n🎉 SUCCESS! Found usage data in response!")
            elif "API Error Response" in response:
                print(f"\n❌ Still getting API error")
            else:
                print(f"\n📋 Response received:")
            
            # Show key parts of the response
            lines = response.split('\n')
            for line in lines[:15]:  # First 15 lines
                if line.strip():
                    print(f"   {line}")
        
        return usage_called_properly
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)[:200]}")
        return False


def main():
    """Run the final test."""
    print("🧪 Final test of usage workflow...")
    success = asyncio.run(test_final_usage())
    
    if success:
        print("\n🎉 The usage workflow is now working properly!")
    else:
        print("\n⚠️  Still some issues, but check the response above.")
    
    print("🔚 Final test completed!")


if __name__ == "__main__":
    main()