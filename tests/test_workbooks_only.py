#!/usr/bin/env python3
"""
Test getting workbooks without usage stats to isolate the issue.
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from meccaai.apps.gradio_app import GradioBedrockApp


async def test_workbooks_only():
    """Test getting workbooks without usage stats."""
    print("=== TESTING WORKBOOKS ONLY (NO USAGE STATS) ===")
    
    app = GradioBedrockApp()
    
    # Ask for workbooks without usage stats
    test_question = "List all workbooks on the Tableau site with their names, IDs, and owners. Do not try to get usage statistics."
    
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
                print(f"   {i}. {status} {tool_name}")
                
                # Check if get_content_usage was called
                if tool_name == 'get_content_usage':
                    print(f"      - ⚠️  get_content_usage was called even though we said not to!")
        
        # Check the response
        if updated_history and len(updated_history) > 1:
            response = updated_history[-1]['content']
            if "workbook" in response.lower() and "API Error" not in response:
                print(f"\n✅ SUCCESS: Got workbook data without API errors")
                # Show first few workbooks
                lines = response.split('\n')[:10]
                for line in lines:
                    if line.strip():
                        print(f"   {line[:100]}...")
            else:
                print(f"\n❌ ISSUE: Response doesn't look like workbook data")
                print(f"Response preview: {response[:200]}...")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Run the workbooks-only test."""
    print("🧪 Testing workbooks without usage stats...")
    asyncio.run(test_workbooks_only())
    print("\n🔚 Workbooks test completed!")


if __name__ == "__main__":
    main()