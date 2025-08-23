#!/usr/bin/env python3
"""
Debug script for content usage API to test different content types and find the issue.
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from meccaai.tools.tableau_tools import get_content_usage, get_workbooks, get_views_on_site


async def debug_content_usage():
    """Debug content usage with different content types."""
    print("=" * 80)
    print("DEBUG: Tableau Content Usage API - Testing Different Content Types")
    print("=" * 80)
    
    try:
        # Step 1: Get workbooks
        print("\n1. Getting workbooks from the site...")
        print("-" * 50)
        
        workbooks_result = await get_workbooks.call()
        
        if not workbooks_result.success or not workbooks_result.result:
            print("❌ Failed to get workbooks")
            return
        
        # Handle nested ToolResult structure
        if hasattr(workbooks_result.result, 'result'):
            workbooks_data = workbooks_result.result.result
        else:
            workbooks_data = workbooks_result.result
            
        workbooks = workbooks_data.get("workbooks", [])
        total_workbooks = workbooks_data.get("total_workbooks", 0)
        
        print(f"✅ Found {total_workbooks} workbooks")
        
        if workbooks:
            print(f"\nFirst 3 workbooks:")
            for i, wb in enumerate(workbooks[:3], 1):
                wb_id = wb.get("id", "N/A")
                wb_name = wb.get("name", "Unknown")
                owner = wb.get("owner", {})
                owner_name = owner.get("name", "Unknown") if owner else "Unknown"
                print(f"  {i}. {wb_name} (ID: {wb_id}) - Owner: {owner_name}")
        
        # Step 2: Test usage API with workbook content type
        print(f"\n2. Testing content usage API with WORKBOOK content type...")
        print("-" * 50)
        
        if len(workbooks) >= 2:
            # Test with workbooks
            content_items = []
            for wb in workbooks[:2]:
                wb_id = wb.get("id")
                if wb_id:
                    content_items.append({
                        "contentType": "workbook",  # Use workbook instead of view
                        "luid": wb_id
                    })
                    wb_name = wb.get("name", "Unknown")
                    print(f"  - Adding workbook: {wb_name} (LUID: {wb_id})")
            
            print(f"\n  Testing usage API with {len(content_items)} workbooks...")
            usage_result = await get_content_usage.call(content_items=content_items)
            
            if usage_result.success:
                print("  ✅ SUCCESS with workbook content type!")
                
                # Handle nested ToolResult structure
                if hasattr(usage_result.result, 'result'):
                    usage_data = usage_result.result.result.get("content_usage", {})
                else:
                    usage_data = usage_result.result.get("content_usage", {})
                
                content_items_response = usage_data.get("content_items", [])
                errors = usage_data.get("errors", [])
                
                print(f"  📊 Response: {len(content_items_response)} content items, {len(errors)} errors")
                
                if content_items_response:
                    print(f"\n  Usage data for workbooks:")
                    for item in content_items_response:
                        content = item.get("content", {})
                        usage = item.get("usage", {})
                        luid = content.get("luid", "N/A")
                        total_hits = usage.get("hitsTotal", "0")
                        
                        # Find workbook name from our original data
                        wb_name = "Unknown"
                        for wb in workbooks:
                            if wb.get("id") == luid:
                                wb_name = wb.get("name", "Unknown")
                                break
                        
                        print(f"    - {wb_name} (LUID: {luid}): {total_hits} total views")
                else:
                    print("  ⚠️  Empty content_items in response")
                    
            else:
                print("  ❌ Failed with workbook content type")
        
        # Step 3: Test with views as well for comparison
        print(f"\n3. Testing content usage API with VIEW content type...")
        print("-" * 50)
        
        views_result = await get_views_on_site.call()
        
        if views_result.success:
            # Handle nested ToolResult structure
            if hasattr(views_result.result, 'result'):
                views_data = views_result.result.result
            else:
                views_data = views_result.result
                
            views = views_data.get("views", [])
            
            if len(views) >= 2:
                content_items_views = []
                for view in views[:2]:
                    view_id = view.get("id")
                    if view_id:
                        content_items_views.append({
                            "contentType": "view",
                            "luid": view_id
                        })
                        view_name = view.get("name", "Unknown")
                        print(f"  - Adding view: {view_name} (LUID: {view_id})")
                
                print(f"\n  Testing usage API with {len(content_items_views)} views...")
                usage_result_views = await get_content_usage.call(content_items=content_items_views)
                
                if usage_result_views.success:
                    print("  ✅ SUCCESS with view content type!")
                    
                    # Handle nested ToolResult structure
                    if hasattr(usage_result_views.result, 'result'):
                        usage_data_views = usage_result_views.result.result.get("content_usage", {})
                    else:
                        usage_data_views = usage_result_views.result.get("content_usage", {})
                    
                    content_items_response = usage_data_views.get("content_items", [])
                    print(f"  📊 Response: {len(content_items_response)} content items")
                    
                    if content_items_response:
                        print(f"\n  Usage data for views:")
                        for item in content_items_response:
                            content = item.get("content", {})
                            usage = item.get("usage", {})
                            luid = content.get("luid", "N/A")
                            total_hits = usage.get("hitsTotal", "0")
                            
                            # Find view name from our original data
                            view_name = "Unknown"
                            for view in views:
                                if view.get("id") == luid:
                                    view_name = view.get("name", "Unknown")
                                    break
                            
                            print(f"    - {view_name} (LUID: {luid}): {total_hits} total views")
                    
                else:
                    print("  ❌ Failed with view content type")
        
        print(f"\n{'=' * 80}")
        print("DEBUG COMPLETED")
        print(f"{'=' * 80}")
    
    except Exception as e:
        print(f"❌ Debug failed with error: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """Main function."""
    print("Starting Content Usage API Debug...")
    print("This will test both workbook and view content types")
    
    await debug_content_usage()


if __name__ == "__main__":
    asyncio.run(main())