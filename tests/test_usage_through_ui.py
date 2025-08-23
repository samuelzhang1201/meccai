#!/usr/bin/env python3
"""
Test the fixed usage API through the UI.
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from meccaai.apps.gradio_app import GradioBedrockApp


async def test_usage_through_ui():
    """Test usage API through the Gradio UI."""
    print("=== TESTING USAGE API THROUGH UI ===")
    
    app = GradioBedrockApp()
    
    # Test the exact question that was failing
    test_question = "show me the workbook content with times viewed by users less than 20 times, show me workbook name, owner, viewed times"
    
    print(f"📝 Testing question: '{test_question}'")
    
    history = []
    
    try:
        updated_history, empty_msg, tool_calls_html = await app.chat(
            test_question, history, "🎯 Data Manager (Coordinator)"
        )
        
        print(f"\n📊 RESULTS:")
        print(f"   - History entries: {len(updated_history)}")
        print(f"   - Tool calls made: {len(app.current_tool_calls)}")
        
        if app.current_tool_calls:
            print(f"\n🔧 TOOLS EXECUTED:")
            for i, tool_call in enumerate(app.current_tool_calls, 1):
                tool_name = tool_call.get('tool_name', 'Unknown')
                success = tool_call.get('tool_result', {}).get('success', False)
                status = "✅" if success else "❌"
                
                tool_input = tool_call.get('tool_input', {})
                
                print(f"   {i}. {status} {tool_name}")
                
                # Check specific tools
                if tool_name == 'get_content_usage':
                    content_items = tool_input.get('content_items', [])
                    print(f"      - Content items: {len(content_items)}")
                    if success:
                        print(f"      - ✅ Usage API call succeeded!")
                    else:
                        print(f"      - ❌ Usage API call failed")
                        
                elif tool_name == 'get_workbooks':
                    if success:
                        print(f"      - ✅ Workbooks retrieved successfully")
        
        # Check the final response
        if updated_history and len(updated_history) > 1:
            response = updated_history[-1]['content']
            
            if "API Error Response" in response:
                print(f"\n❌ STILL GETTING API ERROR")
                print("The fix didn't work properly")
            elif "hitsTotal" in response or "viewed" in response.lower():
                print(f"\n🎉 SUCCESS! Got usage data!")
                # Show a preview
                response_lines = response.split('\n')[:10]
                for line in response_lines:
                    if line.strip():
                        print(f"   {line}")
            elif "cannot get the view counts" in response.lower():
                print(f"\n⚠️  Agent acknowledging limitation but handling gracefully")
            else:
                print(f"\n🤔 Unclear response:")
                print(f"   {response[:200]}...")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Run the UI test."""
    print("🧪 Testing usage API through UI...")
    asyncio.run(test_usage_through_ui())
    print("\n🔚 UI test completed!")


if __name__ == "__main__":
    main()