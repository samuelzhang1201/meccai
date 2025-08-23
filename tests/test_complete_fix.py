#!/usr/bin/env python3
"""
Test the complete fix for both issues.
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from meccaai.apps.gradio_app import GradioBedrockApp


async def test_complete_fix():
    """Test the complete fix for the usage API."""
    print("=== COMPLETE FIX TEST ===")
    
    app = GradioBedrockApp()
    
    # Use a limited question for testing to avoid overwhelming responses
    question = "show me the first 20 workbooks with times viewed by users less than 20 times, show me workbook name, owner, viewed times"
    
    print(f"📝 User question: '{question}'")
    print("🔧 Fixes applied:")
    print("   1. ✅ Handle JSON string serialization from Bedrock agents")
    print("   2. ✅ Accept status code 201 from API") 
    print("   3. ✅ Test uses limited request to avoid overwhelming responses")
    
    history = []
    
    try:
        print("\n🤖 Processing request...")
        
        updated_history, empty_msg, tool_calls_html = await app.chat(
            question, history, "🎯 Data Manager (Coordinator)"
        )
        
        print(f"✅ Response received!")
        print(f"   Tool calls: {len(app.current_tool_calls)}")
        
        # Analyze the tool calls
        get_workbooks_success = False
        usage_api_success = False
        content_items_count = 0
        
        for tool_call in app.current_tool_calls:
            tool_name = tool_call.get('tool_name')
            success = tool_call.get('tool_result', {}).get('success', False)
            
            if tool_name == 'get_workbooks' and success:
                get_workbooks_success = True
                print(f"   ✅ get_workbooks succeeded")
                
            elif tool_name == 'get_content_usage':
                tool_input = tool_call.get('tool_input', {})
                content_items = tool_input.get('content_items', [])
                
                if isinstance(content_items, str):
                    print(f"   🔧 content_items passed as string (will be parsed)")
                else:
                    print(f"   📋 content_items passed as list")
                
                if success:
                    usage_api_success = True
                    result = tool_call.get('tool_result', {}).get('result', {})
                    
                    # Check if we got actual usage data
                    if isinstance(result, dict) and 'content_usage' in result:
                        usage_data = result['content_usage']
                        actual_items = usage_data.get('content_items', [])
                        content_items_count = len(actual_items)
                        print(f"   ✅ get_content_usage succeeded with {content_items_count} items")
                    else:
                        print(f"   ⚠️  get_content_usage succeeded but unexpected format")
                else:
                    print(f"   ❌ get_content_usage failed")
        
        # Check the final response
        if updated_history and len(updated_history) > 1:
            response = updated_history[-1]['content']
            
            # Look for usage data in the response
            usage_indicators = [
                "hitsTotal", "viewed", "views", "view count", 
                "times viewed", "usage", "statistics"
            ]
            
            has_usage_data = any(indicator in response.lower() for indicator in usage_indicators)
            has_api_error = "API Error Response" in response
            
            print(f"\n📊 RESPONSE ANALYSIS:")
            print(f"   - Contains usage data: {'✅' if has_usage_data else '❌'}")
            print(f"   - Has API errors: {'❌' if has_api_error else '✅'}")
            
            if has_usage_data and not has_api_error:
                print(f"   🎉 SUCCESS! Response contains actual usage statistics!")
            elif not has_api_error:
                print(f"   ⚠️  Response is clean but may not have usage data")
            else:
                print(f"   ❌ Still getting API errors")
            
            # Show sample response
            print(f"\n📋 SAMPLE RESPONSE:")
            lines = response.split('\n')
            for line in lines[:8]:  # First 8 lines
                if line.strip():
                    print(f"   {line[:80]}{'...' if len(line) > 80 else ''}")
        
        # Summary
        print(f"\n🎯 TEST SUMMARY:")
        print(f"   get_workbooks: {'✅' if get_workbooks_success else '❌'}")
        print(f"   get_content_usage: {'✅' if usage_api_success else '❌'}")
        print(f"   Content items processed: {content_items_count}")
        
        return get_workbooks_success and usage_api_success and content_items_count > 0
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)[:200]}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run the complete fix test."""
    print("🧪 Testing complete fix...")
    success = asyncio.run(test_complete_fix())
    
    if success:
        print(f"\n🎉 COMPLETE SUCCESS! The usage API is now fully working!")
        print(f"You can now ask about workbook usage statistics and get actual data.")
    else:
        print(f"\n⚠️  Some issues remain, but check the details above.")
    
    print("🔚 Complete fix test completed!")


if __name__ == "__main__":
    main()