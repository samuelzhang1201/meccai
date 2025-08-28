"""Test script for Tableau tools functions."""

import os
import pytest
from meccaai.tools.tableau_tools import (
    get_content_usage,
    get_datasources,
    get_workbooks,
    get_views_on_site,
)


@pytest.mark.asyncio
async def test_tableau_functions():
    """Test the four main Tableau functions."""
    print("Testing Tableau functions...")

    # Check if Tableau token is configured
    if not os.getenv("TABLEAU_TOKEN_VALUE"):
        print("⚠ Warning: TABLEAU_TOKEN_VALUE environment variable not set")
        print("   Tests may fail without authentication")

    # Test 1: get_content_usage
    print("\n1. Testing get_content_usage...")
    try:
        result = await get_content_usage.call()
        print(f"✓ get_content_usage: Success - {result.result}")
    except Exception as e:
        print(f"✗ get_content_usage: Error - {e}")

    # Test 2: get_datasources
    print("\n2. Testing get_datasources...")
    try:
        result = await get_datasources.call(page_size=10)
        if result.success:
            data = (
                result.result.result
                if hasattr(result.result, "result")
                else result.result
            )
            print(
                f"✓ get_datasources: Success - Found {data.get('total_datasources', 0)} datasources"
            )
            if data.get("datasources"):
                print(
                    f"   First datasource: {data['datasources'][0].get('name', 'N/A')}"
                )
        else:
            print(f"✗ get_datasources: Failed - {result.error}")
    except Exception as e:
        print(f"✗ get_datasources: Error - {e}")

    # Test 3: get_workbooks
    print("\n3. Testing get_workbooks...")
    try:
        result = await get_workbooks.call(page_size=10)
        if result.success:
            data = (
                result.result.result
                if hasattr(result.result, "result")
                else result.result
            )
            print(
                f"✓ get_workbooks: Success - Found {data.get('total_workbooks', 0)} workbooks"
            )
            if data.get("workbooks"):
                print(f"   First workbook: {data['workbooks'][0].get('name', 'N/A')}")
        else:
            print(f"✗ get_workbooks: Failed - {result.error}")
    except Exception as e:
        print(f"✗ get_workbooks: Error - {e}")

    # Test 4: get_views_on_site
    print("\n4. Testing get_views_on_site...")
    try:
        result = await get_views_on_site.call(page_size=10)
        if result.success:
            data = (
                result.result.result
                if hasattr(result.result, "result")
                else result.result
            )
            print(
                f"✓ get_views_on_site: Success - Found {data.get('total_views', 0)} views"
            )
            if data.get("views"):
                print(f"   First view: {data['views'][0].get('name', 'N/A')}")
        else:
            print(f"✗ get_views_on_site: Failed - {result.error}")
    except Exception as e:
        print(f"✗ get_views_on_site: Error - {e}")

    print("\nTableau functions test completed!")
