#!/usr/bin/env python3
"""
Simple test script for the updated get_content_usage tool.

This demonstrates how to:
1. Get views from the site
2. Use those view LUIDs to get content usage statistics

Note: This requires proper Tableau Cloud credentials and only works with Tableau Cloud (not Tableau Server).
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from meccaai.tools.tableau_tools import get_content_usage, get_views_on_site


async def demo_content_usage():
    """Demonstrate content usage statistics retrieval."""
    print("=" * 60)
    print("Tableau Content Usage Demo")
    print("=" * 60)
    
    try:
        print("\n1. Getting views on the site...")
        print("-" * 40)
        
        # Get views first (this will help us get LUIDs for usage stats)
        views_result = await get_views_on_site()
        
        if views_result.success and views_result.result:
            views_data = views_result.result
            total_views = views_data.get("total_views", 0)
            views = views_data.get("views", [])
            
            print(f"✅ Found {total_views} views on the site")
            
            if views:
                # Show first few views
                print(f"\nFirst 3 views:")
                for i, view in enumerate(views[:3], 1):
                    view_id = view.get("id", "N/A")
                    view_name = view.get("name", "Unknown")
                    workbook_name = view.get("workbook", {}).get("name", "Unknown")
                    print(f"  {i}. {view_name} (ID: {view_id}) in workbook: {workbook_name}")
                
                print(f"\n2. Getting content usage statistics...")
                print("-" * 40)
                
                # Test 1: Get usage for empty content items (this may fail as it might not be supported)
                print("Testing with empty content items (this may fail as API might require specific content)...")
                try:
                    usage_result_empty = await get_content_usage()
                    
                    if usage_result_empty.success:
                        print("✅ Successfully called get_content_usage() with empty content")
                        usage_data = usage_result_empty.result.get("content_usage", {})
                        print(f"Response keys: {list(usage_data.keys()) if usage_data else 'Empty response'}")
                    else:
                        print("❌ Failed to get usage statistics with empty content")
                        
                except Exception as e:
                    print(f"⚠️  Expected error with empty content: {e}")
                    print("   This is normal - the API likely requires specific content items")
                
                # Test 2: Get usage for specific views (if we have view LUIDs)
                if len(views) > 0:
                    print(f"\nTesting with specific view LUIDs...")
                    
                    # Prepare content items for the first 2 views
                    content_items = []
                    for view in views[:2]:
                        view_id = view.get("id")
                        if view_id:
                            content_items.append({
                                "contentType": "view",
                                "luid": view_id
                            })
                    
                    if content_items:
                        print(f"Requesting usage for {len(content_items)} views...")
                        usage_result_specific = await get_content_usage(content_items)
                        
                        if usage_result_specific.success:
                            print("✅ Successfully got usage statistics for specific views")
                            usage_data = usage_result_specific.result.get("content_usage", {})
                            print(f"Response keys: {list(usage_data.keys()) if usage_data else 'Empty response'}")
                        else:
                            print("❌ Failed to get usage statistics for specific views")
                    else:
                        print("⚠️  No valid view LUIDs found to test with")
            else:
                print("⚠️  No views found on the site")
        else:
            print("❌ Failed to get views from the site")
            if hasattr(views_result, 'error'):
                print(f"Error: {views_result.error}")
    
    except Exception as e:
        print(f"❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\n{'=' * 60}")
    print("Demo completed")
    print(f"{'=' * 60}")


async def main():
    """Main function."""
    print("Starting Tableau Content Usage Demo...")
    print("Note: This requires Tableau Cloud credentials in your environment")
    print("(TABLEAU_TOKEN_VALUE and proper settings in config)")
    
    await demo_content_usage()


if __name__ == "__main__":
    asyncio.run(main())