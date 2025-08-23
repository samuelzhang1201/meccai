#!/usr/bin/env python3
"""
Test the complete workbook usage analysis workflow.
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from meccaai.apps.gradio_app import GradioBedrockApp


async def test_workbook_usage_workflow():
    """Test the complete workbook usage workflow."""
    print("=== TESTING WORKBOOK USAGE ANALYSIS WORKFLOW ===")
    
    app = GradioBedrockApp()
    
    # The problematic question that should work
    test_question = "show me the workbook content with times viewed by users less than 100 times, show me the content name, uid, and view numbers, with its owner's name"
    
    print(f"📝 Testing question: '{test_question}'")
    print("🔍 Expected workflow:")
    print("   1. Get all workbooks using get_workbooks")
    print("   2. Get usage stats for each workbook using get_content_usage")
    print("   3. Filter workbooks with <100 views")
    print("   4. Display results with names, UIDs, view counts, and owner names")
    
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
                
                # Get tool input for debugging
                tool_input = tool_call.get('tool_input', {})
                
                print(f"   {i}. {status} {tool_name}")
                if tool_name == 'get_content_usage':
                    content_items = tool_input.get('content_items', [])
                    print(f"      - Content items provided: {len(content_items)}")
                    if not content_items:
                        print("      - ⚠️  WARNING: No content items provided to get_content_usage!")
        
        # Check the final response
        if updated_history and len(updated_history) > 1:
            response = updated_history[-1]['content']
            if "API Error Response" in response:
                print(f"\n❌ WORKFLOW FAILED:")
                print("   - get_content_usage called with empty content_items")
                print("   - Need to call get_workbooks first, then get_content_usage with workbook IDs")
            elif "content_items\": []" in response:
                print(f"\n❌ EMPTY RESULTS:")
                print("   - API returned empty results")
                print("   - This confirms get_content_usage was called without proper workbook IDs")
            else:
                print(f"\n✅ WORKFLOW SUCCESS:")
                print("   - Got workbook usage data")
                response_preview = response[:200] + "..." if len(response) > 200 else response
                print(f"   - Response preview: {response_preview}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Run the workflow test."""
    print("🧪 Testing workbook usage analysis workflow...")
    asyncio.run(test_workbook_usage_workflow())
    print("\n🔚 Workflow test completed!")


if __name__ == "__main__":
    main()