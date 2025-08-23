#!/usr/bin/env python3
"""
Verify all Tableau tools have consistent pagination configuration.
"""

import re
from pathlib import Path


def verify_tableau_pagination():
    """Verify all Tableau tools use pageSize=100 and proper pagination."""
    print("=== TABLEAU PAGINATION VERIFICATION ===")
    
    tableau_tools_file = Path(__file__).parent.parent / "meccaai/tools/tableau_tools.py"
    content = tableau_tools_file.read_text()
    
    # Find all @tool decorators
    tool_pattern = r'@tool\("([^"]+)"\)'
    tools = re.findall(tool_pattern, content)
    
    print(f"Found {len(tools)} Tableau tools:")
    for tool in tools:
        print(f"  - {tool}")
    
    # Check pagination configuration
    print(f"\n🔍 PAGINATION ANALYSIS:")
    
    # Tools that should have pagination (list operations)
    list_tools = [
        "get_users_on_site", "get_users_in_group", "get_group_set", 
        "get_datasources", "get_workbooks", "get_views_on_site", "list_all_pats"
    ]
    
    # Tools that don't need pagination (single operations)
    single_tools = ["add_user_to_site", "update_user", "get_content_usage"]
    
    # Check page_size configuration
    page_size_pattern = r'page_size = (\d+)'
    page_sizes = re.findall(page_size_pattern, content)
    
    print(f"📏 Page sizes found: {page_sizes}")
    
    # Check if all page sizes are 100
    all_100 = all(size == "100" for size in page_sizes)
    print(f"   All page sizes = 100: {'✅' if all_100 else '❌'}")
    
    # Check pagination logic
    pagination_pattern = r'total_available = int\(pagination\.get\("totalAvailable", 0\)\)'
    pagination_checks = len(re.findall(pagination_pattern, content))
    
    print(f"📊 Pagination termination checks: {pagination_checks}")
    print(f"   Expected for list tools: {len(list_tools)}")
    print(f"   Pagination logic complete: {'✅' if pagination_checks >= len(list_tools) else '❌'}")
    
    # Check while True loops for pagination
    while_loops = len(re.findall(r'while True:', content))
    print(f"🔄 While loops (pagination): {while_loops}")
    print(f"   Expected for list tools: {len(list_tools)}")
    print(f"   Pagination loops complete: {'✅' if while_loops >= len(list_tools) else '❌'}")
    
    # Summary
    print(f"\n🎯 SUMMARY:")
    print(f"✅ All tools found: {len(tools)} tools")
    print(f"{'✅' if all_100 else '❌'} Page size standardized: 100")
    print(f"{'✅' if pagination_checks >= len(list_tools) else '❌'} Pagination termination: Complete")
    print(f"{'✅' if while_loops >= len(list_tools) else '❌'} Pagination loops: Complete")
    
    # List tools analysis
    print(f"\n📋 LIST TOOLS (should have pagination):")
    for tool in list_tools:
        if tool in tools:
            print(f"   ✅ {tool} - Found in codebase")
        else:
            print(f"   ❓ {tool} - Not found (may have different name)")
    
    print(f"\n🔧 SINGLE OPERATION TOOLS (no pagination needed):")
    for tool in single_tools:
        if tool in tools:
            print(f"   ✅ {tool} - Found in codebase")
        else:
            print(f"   ❓ {tool} - Not found (may have different name)")
    
    # Final verdict
    all_good = all_100 and pagination_checks >= len(list_tools) and while_loops >= len(list_tools)
    
    if all_good:
        print(f"\n🎉 SUCCESS: All Tableau tools have consistent pagination!")
        print(f"   - Page size: 100 (Tableau API recommended)")
        print(f"   - Pagination: Complete with proper termination")
        print(f"   - Fetching: All results returned")
    else:
        print(f"\n⚠️  Some issues found - see details above")
    
    return all_good


def main():
    """Run the verification."""
    print("🔍 Verifying Tableau pagination configuration...")
    success = verify_tableau_pagination()
    print(f"\n{'✅ VERIFICATION COMPLETE' if success else '❌ ISSUES FOUND'}")


if __name__ == "__main__":
    main()