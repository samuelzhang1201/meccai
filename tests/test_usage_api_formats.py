#!/usr/bin/env python3
"""
Test different payload formats for the Tableau content usage API.
"""

import asyncio
import sys
import httpx
from pathlib import Path
from urllib.parse import urljoin

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from meccaai.tools.tableau_tools import TableauAuthManager
from meccaai.core.logging import get_logger

logger = get_logger(__name__)


async def test_usage_api_formats():
    """Test different payload formats for the usage API."""
    print("=== TESTING TABLEAU USAGE API FORMATS ===")
    
    auth_manager = TableauAuthManager()
    
    try:
        # Sign in first
        await auth_manager.sign_in()
        print("✅ Authenticated successfully")
        
        # Get some sample workbooks to test with
        workbooks_url = urljoin(auth_manager.server_url, f"/api/{auth_manager.api_version}/sites/{auth_manager.site_id}/workbooks")
        
        async with httpx.AsyncClient() as client:
            workbooks_response = await client.get(
                workbooks_url,
                headers=auth_manager.get_auth_headers()
            )
            
            if workbooks_response.status_code == 200:
                workbooks_data = workbooks_response.json()
                workbooks = workbooks_data.get("workbooks", {}).get("workbook", [])
                
                if workbooks:
                    sample_workbook = workbooks[0]
                    workbook_id = sample_workbook.get("id")
                    workbook_name = sample_workbook.get("name")
                    print(f"✅ Got sample workbook: {workbook_name} (ID: {workbook_id})")
                    
                    # Now test different usage API formats
                    usage_url = urljoin(auth_manager.server_url, "/api/-/content/usage-stats")
                    
                    # Test different payload formats
                    test_payloads = [
                        # Format 1: Simple array
                        {
                            "name": "Simple content_items array",
                            "payload": {"content_items": [{"luid": workbook_id, "type": "workbook"}]}
                        },
                        # Format 2: With additional fields
                        {
                            "name": "With content type specification",
                            "payload": {"content_items": [{"luid": workbook_id, "contentType": "workbook"}]}
                        },
                        # Format 3: Different structure
                        {
                            "name": "Alternative structure",
                            "payload": {"contentItems": [{"id": workbook_id, "type": "workbook"}]}
                        },
                        # Format 4: With time range
                        {
                            "name": "With usage period",
                            "payload": {
                                "content_items": [{"luid": workbook_id, "type": "workbook"}],
                                "usage_period_days": 30
                            }
                        },
                        # Format 5: Array of IDs only
                        {
                            "name": "ID array only",
                            "payload": {"content_ids": [workbook_id]}
                        },
                    ]
                    
                    for i, test_case in enumerate(test_payloads, 1):
                        print(f"\n🧪 Test {i}: {test_case['name']}")
                        
                        try:
                            response = await client.post(
                                usage_url,
                                json=test_case['payload'],
                                headers={
                                    **auth_manager.get_auth_headers(),
                                    "Content-Type": "application/vnd.tableau.usagestats.v1.BatchGetUsageRequest+json",
                                    "Accept": "application/vnd.tableau.usagestats.v1.ContentItemUsageStatsList+json",
                                },
                                timeout=30.0
                            )
                            
                            print(f"   Status: {response.status_code}")
                            print(f"   Payload: {test_case['payload']}")
                            
                            if response.status_code == 200:
                                data = response.json()
                                content_items = data.get('content_items', [])
                                print(f"   ✅ SUCCESS! Got {len(content_items)} content items")
                                if content_items:
                                    print(f"   Sample item keys: {list(content_items[0].keys())}")
                                    return  # Found working format
                            else:
                                error_text = response.text[:200]
                                print(f"   ❌ Failed: {error_text}")
                                
                        except Exception as e:
                            print(f"   ❌ Exception: {str(e)[:100]}")
                    
                    print(f"\n❌ All payload formats failed")
                    
                else:
                    print("❌ No workbooks found to test with")
            else:
                print(f"❌ Failed to get workbooks: {workbooks_response.status_code}")
    
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await auth_manager.sign_out()


def main():
    """Run the format tests."""
    print("🧪 Testing Tableau usage API payload formats...")
    asyncio.run(test_usage_api_formats())
    print("\n🔚 Format tests completed!")


if __name__ == "__main__":
    main()