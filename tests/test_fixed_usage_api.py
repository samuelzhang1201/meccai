#!/usr/bin/env python3
"""
Test the fixed content usage API implementation.
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from meccaai.tools.tableau_tools import get_workbooks, get_content_usage


async def test_fixed_usage_api():
    """Test the fixed content usage API."""
    print("=== TESTING FIXED CONTENT USAGE API ===")
    
    try:
        # First get workbooks
        print("1. Getting workbooks...")
        workbooks_result = await get_workbooks.func()
        
        if workbooks_result.success:
            workbooks_data = workbooks_result.result
            workbooks = workbooks_data.get("workbooks", [])
            
            if workbooks:
                print(f"   ✅ Got {len(workbooks)} workbooks")
                
                # Take the first few workbooks to test usage
                test_workbooks = workbooks[:3]  # Test with 3 workbooks
                
                # Format them for the usage API
                content_items = []
                for wb in test_workbooks:
                    content_items.append({
                        "luid": wb["id"],
                        "type": "workbook"
                    })
                
                print(f"2. Getting usage stats for {len(content_items)} workbooks...")
                print(f"   Testing workbooks: {[wb['name'] for wb in test_workbooks]}")
                
                # Now test the usage API with proper content items
                usage_result = await get_content_usage.func(content_items=content_items)
                
                if usage_result.success:
                    usage_data = usage_result.result.get("content_usage", {})
                    usage_items = usage_data.get("content_items", [])
                    
                    print(f"   ✅ SUCCESS! Got usage data for {len(usage_items)} items")
                    
                    # Show sample usage data
                    for i, item in enumerate(usage_items[:2]):  # Show first 2 items
                        content = item.get("content", {})
                        usage = item.get("usage", {})
                        
                        workbook_name = next((wb["name"] for wb in test_workbooks if wb["id"] == content.get("luid")), "Unknown")
                        hits_total = usage.get("hitsTotal", "0")
                        hits_recent = usage.get("hitsLastTwoWeeksTotal", "0")
                        
                        print(f"      Workbook: {workbook_name}")
                        print(f"      Total views: {hits_total}")
                        print(f"      Recent views (2 weeks): {hits_recent}")
                        print()
                    
                    # Test filtering workbooks with <20 views
                    low_usage_workbooks = []
                    for item in usage_items:
                        usage = item.get("usage", {})
                        hits_total = int(usage.get("hitsTotal", "0"))
                        
                        if hits_total < 20:
                            content = item.get("content", {})
                            workbook_name = next((wb["name"] for wb in test_workbooks if wb["id"] == content.get("luid")), "Unknown")
                            owner = next((wb.get("owner", {}).get("name", "Unknown") for wb in test_workbooks if wb["id"] == content.get("luid")), "Unknown")
                            
                            low_usage_workbooks.append({
                                "name": workbook_name,
                                "owner": owner,
                                "views": hits_total,
                                "id": content.get("luid")
                            })
                    
                    print(f"🎯 WORKBOOKS WITH <20 VIEWS:")
                    if low_usage_workbooks:
                        for wb in low_usage_workbooks:
                            print(f"   • {wb['name']} - {wb['views']} views - Owner: {wb['owner']}")
                    else:
                        print("   No workbooks found with <20 views in the sample")
                    
                    return True  # Success!
                    
                else:
                    print(f"   ❌ Usage API failed: {usage_result}")
                    return False
                    
            else:
                print("   ❌ No workbooks found")
                return False
        else:
            print(f"   ❌ Failed to get workbooks: {workbooks_result}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run the test."""
    print("🧪 Testing fixed usage API...")
    success = asyncio.run(test_fixed_usage_api())
    
    if success:
        print("\n🎉 SUCCESS! The usage API is now working!")
    else:
        print("\n❌ The API still has issues.")
    
    print("🔚 Test completed!")


if __name__ == "__main__":
    main()