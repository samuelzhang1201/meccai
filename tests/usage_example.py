#!/usr/bin/env python3
"""
Simple usage example for the get_content_usage tool.

This script demonstrates the correct way to call the updated get_content_usage tool
with proper content items that include contentType and luid.
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from meccaai.tools.tableau_tools import get_content_usage, get_views_on_site


async def demo_usage_example():
    """Demonstrate correct usage of get_content_usage with proper content items."""
    print("=" * 60)
    print("Tableau Content Usage - Correct Usage Example")
    print("=" * 60)
    
    try:
        # Step 1: Get some views to use for usage statistics
        print("Step 1: Getting views from the site...")
        views_result = await get_views_on_site.call()
        
        if not views_result.success or not views_result.result:
            print("❌ Failed to get views. Cannot proceed with usage example.")
            return
        
        # Handle nested ToolResult structure
        if hasattr(views_result.result, 'result'):
            views_data = views_result.result.result
        else:
            views_data = views_result.result
            
        views = views_data.get("views", [])
        
        if not views:
            print("❌ No views found on the site. Cannot proceed with usage example.")
            return
            
        print(f"✅ Found {len(views)} views")
        
        # Step 2: Prepare content items in the correct format
        print("\nStep 2: Preparing content items for usage statistics...")
        
        # Take first 2 views and format them correctly
        content_items = []
        for i, view in enumerate(views[:2]):
            view_id = view.get("id")
            view_name = view.get("name", f"View {i+1}")
            
            if view_id:
                content_items.append({
                    "contentType": "view",  # Must be one of: view, workbook, datasource, flow
                    "luid": view_id         # The LUID (ID) of the content item
                })
                print(f"  - Added view: {view_name} (LUID: {view_id})")
        
        if not content_items:
            print("❌ No valid view LUIDs found. Cannot proceed.")
            return
        
        # Step 3: Call get_content_usage with properly formatted content items
        print(f"\nStep 3: Getting usage statistics for {len(content_items)} items...")
        print("Request format:")
        print(f"  URL: /api/-/content/usage-stats")
        print(f"  Method: POST")
        print(f"  Body: {{'contentItems': {content_items}}}")
        
        usage_result = await get_content_usage.call(content_items=content_items)
        
        if usage_result.success:
            print("✅ Successfully retrieved usage statistics!")
            # Handle nested ToolResult structure
            if hasattr(usage_result.result, 'result'):
                usage_data = usage_result.result.result.get("content_usage", {})
            else:
                usage_data = usage_result.result.get("content_usage", {})
            
            print(f"\nResponse structure:")
            if isinstance(usage_data, dict):
                for key, value in usage_data.items():
                    if isinstance(value, list):
                        print(f"  {key}: [{len(value)} items]")
                    else:
                        print(f"  {key}: {type(value).__name__}")
            else:
                print(f"  Type: {type(usage_data).__name__}")
            
            # If the response contains usage data, show a sample
            if usage_data:
                print(f"\nSample data: {str(usage_data)[:200]}...")
            
        else:
            print("❌ Failed to get usage statistics")
            if hasattr(usage_result, 'error') and usage_result.error:
                print(f"Error: {usage_result.error}")
    
    except Exception as e:
        print(f"❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\n{'=' * 60}")
    print("Demo completed")
    print(f"{'=' * 60}")


async def main():
    """Main function."""
    print("Content Usage Example - Correct API Usage")
    print("Note: This requires valid Tableau Cloud credentials")
    print("The API endpoint: POST /api/-/content/usage-stats")
    print("Required payload format: {'contentItems': [{'contentType': 'view', 'luid': 'id'}]}")
    print()
    
    await demo_usage_example()


if __name__ == "__main__":
    asyncio.run(main())