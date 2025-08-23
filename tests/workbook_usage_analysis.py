#!/usr/bin/env python3
"""
Comprehensive analysis of Tableau workbooks with less than 100 views.
Shows content name, uid, view numbers, and owner's name.
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from meccaai.tools.tableau_tools import get_content_usage, get_workbooks


async def analyze_workbook_usage():
    """Find workbooks with less than 100 views and show detailed information."""
    print("=" * 100)
    print("📊 TABLEAU WORKBOOK USAGE ANALYSIS")
    print("Finding workbooks with less than 100 total views")
    print("=" * 100)
    
    try:
        # Step 1: Get all workbooks from the site
        print("\n🔍 Step 1: Retrieving all workbooks from Tableau site...")
        print("-" * 60)
        
        workbooks_result = await get_workbooks.call()
        
        if not workbooks_result.success or not workbooks_result.result:
            print("❌ Failed to retrieve workbooks from site")
            return
        
        # Handle nested ToolResult structure
        if hasattr(workbooks_result.result, 'result'):
            workbooks_data = workbooks_result.result.result
        else:
            workbooks_data = workbooks_result.result
            
        workbooks = workbooks_data.get("workbooks", [])
        total_workbooks = workbooks_data.get("total_workbooks", 0)
        
        print(f"✅ Successfully retrieved {total_workbooks} workbooks from the site")
        
        if not workbooks:
            print("❌ No workbooks found on the site")
            return
        
        # Step 2: Prepare all workbooks for usage statistics
        print(f"\n📈 Step 2: Preparing {len(workbooks)} workbooks for usage analysis...")
        print("-" * 60)
        
        # Process workbooks in batches to avoid API limits
        batch_size = 50  # Process 50 workbooks at a time
        all_usage_results = []
        
        for i in range(0, len(workbooks), batch_size):
            batch = workbooks[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (len(workbooks) + batch_size - 1) // batch_size
            
            print(f"  Processing batch {batch_num}/{total_batches} ({len(batch)} workbooks)...")
            
            # Prepare content items for this batch
            content_items = []
            for wb in batch:
                wb_id = wb.get("id")
                if wb_id:
                    content_items.append({
                        "contentType": "workbook",
                        "luid": wb_id
                    })
            
            if content_items:
                # Get usage statistics for this batch
                usage_result = await get_content_usage.call(content_items=content_items)
                
                if usage_result.success:
                    # Handle nested ToolResult structure
                    if hasattr(usage_result.result, 'result'):
                        usage_data = usage_result.result.result.get("content_usage", {})
                    else:
                        usage_data = usage_result.result.get("content_usage", {})
                    
                    content_items_response = usage_data.get("content_items", [])
                    errors = usage_data.get("errors", [])
                    
                    print(f"    ✅ Batch {batch_num}: {len(content_items_response)} usage records, {len(errors)} errors")
                    all_usage_results.extend(content_items_response)
                else:
                    print(f"    ❌ Batch {batch_num}: Failed to get usage statistics")
        
        # Step 3: Process and analyze the results
        print(f"\n📊 Step 3: Analyzing usage data...")
        print("-" * 60)
        
        print(f"Total usage records retrieved: {len(all_usage_results)}")
        
        # Create a mapping of LUID to workbook details
        workbook_details = {}
        for wb in workbooks:
            wb_id = wb.get("id")
            if wb_id:
                owner = wb.get("owner", {})
                workbook_details[wb_id] = {
                    "name": wb.get("name", "Unknown"),
                    "id": wb_id,
                    "owner_id": owner.get("id", "N/A") if owner else "N/A",
                    "owner_name": owner.get("name", "Unknown") if owner else "Unknown",
                    "created_at": wb.get("createdAt", "N/A"),
                    "updated_at": wb.get("updatedAt", "N/A"),
                    "project_id": wb.get("project", {}).get("id", "N/A") if wb.get("project") else "N/A",
                }
        
        # Find workbooks with less than 100 views
        low_usage_workbooks = []
        
        for item in all_usage_results:
            content = item.get("content", {})
            usage = item.get("usage", {})
            
            luid = content.get("luid")
            content_type = content.get("type")
            
            if content_type == "workbook" and luid:
                total_hits = int(usage.get("hitsTotal", "0"))
                
                if total_hits < 100:
                    workbook_info = workbook_details.get(luid, {})
                    
                    low_usage_workbooks.append({
                        "name": workbook_info.get("name", "Unknown"),
                        "luid": luid,
                        "total_views": total_hits,
                        "views_last_2_weeks": int(usage.get("hitsLastTwoWeeksTotal", "0")),
                        "views_last_month": int(usage.get("hitsLastOneMonthTotal", "0")),
                        "views_last_3_months": int(usage.get("hitsLastThreeMonthsTotal", "0")),
                        "views_last_12_months": int(usage.get("hitsLastTwelveMonthsTotal", "0")),
                        "owner_name": workbook_info.get("owner_name", "Unknown"),
                        "owner_id": workbook_info.get("owner_id", "N/A"),
                        "created_at": workbook_info.get("created_at", "N/A"),
                        "updated_at": workbook_info.get("updated_at", "N/A"),
                    })
        
        # Sort by total views (ascending - lowest usage first)
        low_usage_workbooks.sort(key=lambda x: x["total_views"])
        
        # Step 4: Display results
        print(f"\n🎯 RESULTS: Workbooks with less than 100 total views")
        print("=" * 100)
        print(f"Found {len(low_usage_workbooks)} workbooks with less than 100 views")
        print("=" * 100)
        
        if low_usage_workbooks:
            # Display header
            print(f"\n{'#':<3} {'WORKBOOK NAME':<35} {'LUID':<40} {'VIEWS':<8} {'OWNER':<25}")
            print("-" * 115)
            
            # Display each workbook
            for i, wb in enumerate(low_usage_workbooks, 1):
                name = wb["name"][:32] + "..." if len(wb["name"]) > 35 else wb["name"]
                luid = wb["luid"]
                total_views = wb["total_views"]
                owner = wb["owner_name"][:22] + "..." if len(wb["owner_name"]) > 25 else wb["owner_name"]
                
                print(f"{i:<3} {name:<35} {luid:<40} {total_views:<8} {owner:<25}")
            
            # Display detailed breakdown for first 10 workbooks
            print(f"\n📋 DETAILED BREAKDOWN (First 10 workbooks)")
            print("=" * 100)
            
            for i, wb in enumerate(low_usage_workbooks[:10], 1):
                print(f"\n{i}. {wb['name']}")
                print(f"   LUID: {wb['luid']}")
                print(f"   Owner: {wb['owner_name']} (ID: {wb['owner_id']})")
                print(f"   Usage Statistics:")
                print(f"     • Total views (lifetime): {wb['total_views']}")
                print(f"     • Last 2 weeks: {wb['views_last_2_weeks']}")
                print(f"     • Last month: {wb['views_last_month']}")
                print(f"     • Last 3 months: {wb['views_last_3_months']}")
                print(f"     • Last 12 months: {wb['views_last_12_months']}")
                print(f"   Created: {wb['created_at']}")
                print(f"   Updated: {wb['updated_at']}")
            
            if len(low_usage_workbooks) > 10:
                print(f"\n... and {len(low_usage_workbooks) - 10} more workbooks with low usage")
            
            # Summary statistics
            print(f"\n📈 SUMMARY STATISTICS")
            print("=" * 50)
            total_views = sum(wb["total_views"] for wb in low_usage_workbooks)
            avg_views = total_views / len(low_usage_workbooks) if low_usage_workbooks else 0
            print(f"Total workbooks with <100 views: {len(low_usage_workbooks)}")
            print(f"Total views across all these workbooks: {total_views}")
            print(f"Average views per workbook: {avg_views:.1f}")
            print(f"Workbooks with 0 views: {len([wb for wb in low_usage_workbooks if wb['total_views'] == 0])}")
            print(f"Workbooks with 1-10 views: {len([wb for wb in low_usage_workbooks if 1 <= wb['total_views'] <= 10])}")
            print(f"Workbooks with 11-50 views: {len([wb for wb in low_usage_workbooks if 11 <= wb['total_views'] <= 50])}")
            print(f"Workbooks with 51-99 views: {len([wb for wb in low_usage_workbooks if 51 <= wb['total_views'] <= 99])}")
            
        else:
            print("🎉 Great! All workbooks have 100 or more views!")
        
        print(f"\n{'=' * 100}")
        print("✅ ANALYSIS COMPLETED")
        print(f"{'=' * 100}")
    
    except Exception as e:
        print(f"❌ Analysis failed with error: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """Main function."""
    print("🚀 Starting Tableau Workbook Usage Analysis...")
    print("This will find all workbooks with less than 100 total views")
    print("and display their name, LUID, view count, and owner information.")
    
    await analyze_workbook_usage()


if __name__ == "__main__":
    asyncio.run(main())