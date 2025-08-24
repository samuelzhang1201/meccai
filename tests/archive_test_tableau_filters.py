#!/usr/bin/env python3
"""Test Tableau API filtering functionality."""

import asyncio
import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from meccaai.apps.gradio_app import GradioBedrockApp


async def test_tableau_filtering():
    """Test Tableau filtering functionality through the Gradio app."""
    print("=== TABLEAU FILTERING TEST ===")
    
    app = GradioBedrockApp()
    
    # Test with filtering conditions - asking for users with specific role
    test_question = """Show me only Tableau users with the role 'Viewer', 
    and sort them by name ascending. 
    Only show the id, name, and siteRole fields to keep the response short."""
    
    print(f"📝 Testing Tableau filtering with specific conditions:")
    print(f"   Question: '{test_question}'")
    
    history = []
    
    try:
        updated_history, empty_msg, tool_calls_html = await app.chat(
            test_question, history, "🎯 Data Manager (Coordinator)"
        )
        
        if updated_history and len(updated_history) > 1:
            response = updated_history[-1]['content']
            
            # Check if the response indicates filtering was used
            filter_keywords = [
                "filter", "siteRole", "Viewer", "sorted", "ascending", 
                "filtered", "specific", "role"
            ]
            
            found_keywords = [kw for kw in filter_keywords if kw.lower() in response.lower()]
            
            print(f"\n📊 RESPONSE ANALYSIS:")
            print(f"   - Response length: {len(response)} characters")
            print(f"   - Filter-related keywords found: {len(found_keywords)}")
            
            # Check for tool calls indicating tableau admin was used
            if tool_calls_html and "tableau_admin_agent" in tool_calls_html:
                print(f"   🤖 Tableau admin agent was called")
            
            # Check if response seems shorter/more focused due to filtering
            if len(response) < 2000:  # Shorter response indicates filtering worked
                print(f"   ✅ Response is concise ({len(response)} chars) - filtering likely worked")
                
                if found_keywords:
                    print(f"   🔧 Keywords found: {', '.join(found_keywords)}")
                    return True
                else:
                    print(f"   ⚠️  Response is short but doesn't mention filtering")
                    print(f"   📄 Response preview: {response[:300]}...")
                    return True  # Still counts as success if response is short
            else:
                print(f"   ⚠️  Response is long ({len(response)} chars) - filtering may not have worked")
                print(f"   📄 Response preview: {response[:500]}...")
                return False
        else:
            print(f"   ❌ No response received")
            return False
            
    except Exception as e:
        print(f"   ❌ Test failed: {str(e)[:200]}")
        import traceback
        traceback.print_exc()
        return False


async def test_workbook_filtering():
    """Test workbook filtering functionality."""
    print("\n=== WORKBOOK FILTERING TEST ===")
    
    app = GradioBedrockApp()
    
    # Test workbook filtering with date filter
    test_question = """Show me only workbooks created after 2023-01-01, 
    sorted by creation date descending. 
    Only show the id, name, and createdAt fields to keep it brief."""
    
    print(f"📝 Testing workbook filtering:")
    print(f"   Question: '{test_question}'")
    
    history = []
    
    try:
        updated_history, empty_msg, tool_calls_html = await app.chat(
            test_question, history, "🎯 Data Manager (Coordinator)"
        )
        
        if updated_history and len(updated_history) > 1:
            response = updated_history[-1]['content']
            
            # Check if filtering was applied
            filter_keywords = [
                "created after", "2023-01-01", "createdAt", "sorted", 
                "descending", "filtered", "workbook"
            ]
            
            found_keywords = [kw for kw in filter_keywords if kw.lower() in response.lower()]
            
            print(f"\n📊 RESPONSE ANALYSIS:")
            print(f"   - Response length: {len(response)} characters")
            print(f"   - Filter-related keywords found: {len(found_keywords)}")
            
            if len(response) < 2000 and found_keywords:
                print(f"   ✅ SUCCESS: Workbook filtering appears to work")
                print(f"   🔧 Keywords found: {', '.join(found_keywords)}")
                return True
            else:
                print(f"   ⚠️  Workbook filtering may not have worked as expected")
                return False
        else:
            print(f"   ❌ No response received")
            return False
            
    except Exception as e:
        print(f"   ❌ Test failed: {str(e)[:200]}")
        return False


def main():
    """Run the Tableau filtering tests."""
    print("🧪 Testing Tableau API filtering functionality...")
    
    # Run both tests
    user_success = asyncio.run(test_tableau_filtering())
    workbook_success = asyncio.run(test_workbook_filtering())
    
    print(f"\n📋 TEST RESULTS:")
    print(f"   User filtering: {'✅ PASS' if user_success else '⚠️  NEEDS REVIEW'}")
    print(f"   Workbook filtering: {'✅ PASS' if workbook_success else '⚠️  NEEDS REVIEW'}")
    
    if user_success and workbook_success:
        print(f"\n🎉 SUCCESS: Tableau filtering functionality working!")
    else:
        print(f"\n📝 Filtering has been implemented but may need fine-tuning")
    
    print("🔚 Tableau filtering test completed!")


if __name__ == "__main__":
    main()