#!/usr/bin/env python3
"""
Get detailed response to see what data we're actually receiving.
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from meccaai.apps.gradio_app import GradioBedrockApp


async def test_detailed_response():
    """Test to see the detailed response."""
    print("=== DETAILED RESPONSE TEST ===")
    
    app = GradioBedrockApp()
    
    # Simple question first to get workbooks
    test_question = "Get usage statistics for all workbooks and show me workbooks with less than 20 total views. Include workbook names, owners, and view counts."
    
    print(f"📝 Testing question: '{test_question}'")
    
    history = []
    
    try:
        updated_history, empty_msg, tool_calls_html = await app.chat(
            test_question, history, "🎯 Data Manager (Coordinator)"
        )
        
        print(f"\n📊 RESULTS:")
        print(f"   - Tool calls made: {len(app.current_tool_calls)}")
        
        # Show tool call details
        for i, tool_call in enumerate(app.current_tool_calls, 1):
            tool_name = tool_call.get('tool_name', 'Unknown')
            success = tool_call.get('tool_result', {}).get('success', False)
            
            print(f"\n🔧 Tool {i}: {tool_name} - {'✅' if success else '❌'}")
            
            if tool_name == 'get_content_usage' and success:
                result = tool_call.get('tool_result', {}).get('result', {})
                content_usage = result.get('content_usage', {})
                content_items = content_usage.get('content_items', [])
                
                print(f"   - Got {len(content_items)} content items")
                
                if content_items:
                    # Show sample data structure
                    sample_item = content_items[0]
                    print(f"   - Sample item structure: {list(sample_item.keys())}")
                    
                    if 'content' in sample_item and 'usage' in sample_item:
                        content = sample_item['content']
                        usage = sample_item['usage']
                        print(f"   - Content keys: {list(content.keys())}")
                        print(f"   - Usage keys: {list(usage.keys())}")
                        
                        # Show actual usage values
                        hits_total = usage.get('hitsTotal', '0')
                        hits_recent = usage.get('hitsLastTwoWeeksTotal', '0')
                        print(f"   - Sample hits total: {hits_total}")
                        print(f"   - Sample recent hits: {hits_recent}")
                        
                        # Count low usage workbooks
                        low_usage_count = 0
                        for item in content_items[:10]:  # Check first 10
                            item_usage = item.get('usage', {})
                            total_hits = int(item_usage.get('hitsTotal', '0'))
                            if total_hits < 20:
                                low_usage_count += 1
                        
                        print(f"   - Low usage workbooks (first 10 checked): {low_usage_count}")
        
        # Show the actual response content
        if updated_history and len(updated_history) > 1:
            response = updated_history[-1]['content']
            print(f"\n📝 FULL RESPONSE:")
            print(response[:1000] + "..." if len(response) > 1000 else response)
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Run the detailed test."""
    print("🧪 Getting detailed response...")
    asyncio.run(test_detailed_response())
    print("\n🔚 Detailed test completed!")


if __name__ == "__main__":
    main()