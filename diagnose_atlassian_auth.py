#!/usr/bin/env python3
"""Diagnose Atlassian authentication issues."""

import os
import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from meccaai.core.config import settings
from meccaai.tools.atlassian_tools import AtlassianAuthManager


def check_environment_variables():
    """Check what Atlassian environment variables are set."""
    print("=== ENVIRONMENT VARIABLES CHECK ===")
    
    atlassian_vars = [
        'ATLASSIAN_AUTH_METHOD',
        'JIRA_BASE_URL', 
        'CONFLUENCE_BASE_URL',
        'ATLASSIAN_API_TOKEN',
        'ATLASSIAN_EMAIL',
        'ATLASSIAN_SESSION_TOKEN',
        'ATLASSIAN_COOKIES',
        'ATLASSIAN_OAUTH_TOKEN'
    ]
    
    print("Checking environment variables:")
    for var in atlassian_vars:
        value = os.getenv(var)
        if value:
            # Mask sensitive values
            if 'TOKEN' in var or 'COOKIES' in var:
                masked = value[:8] + "..." + value[-4:] if len(value) > 12 else "***"
                print(f"   ✅ {var}: {masked}")
            else:
                print(f"   ✅ {var}: {value}")
        else:
            print(f"   ❌ {var}: Not set")
    
    return any(os.getenv(var) for var in atlassian_vars)


def check_settings_config():
    """Check how settings are configured."""
    print("\n=== SETTINGS CONFIGURATION CHECK ===")
    
    auth_manager = AtlassianAuthManager()
    
    print("AtlassianAuthManager configuration:")
    print(f"   - Auth method: {auth_manager.auth_method}")
    print(f"   - Jira URL: {auth_manager.jira_base_url}")
    print(f"   - Confluence URL: {auth_manager.confluence_base_url}")
    print(f"   - Has API token: {'Yes' if auth_manager.api_token else 'No'}")
    print(f"   - Has email: {'Yes' if auth_manager.email else 'No'}")
    print(f"   - Has session token: {'Yes' if auth_manager.session_token else 'No'}")
    print(f"   - Has OAuth token: {'Yes' if auth_manager.oauth_token else 'No'}")
    
    return auth_manager


def test_auth_headers(auth_manager):
    """Test what authentication headers would be generated."""
    print("\n=== AUTHENTICATION HEADERS TEST ===")
    
    try:
        headers = auth_manager.get_auth_headers()
        print("Generated headers:")
        for key, value in headers.items():
            if key == "Authorization":
                # Mask the token part
                if "Basic" in value:
                    print(f"   ✅ {key}: Basic {value.split()[-1][:10]}...")
                elif "Bearer" in value:
                    print(f"   ✅ {key}: Bearer {value.split()[-1][:10]}...")
                else:
                    print(f"   ✅ {key}: {value}")
            else:
                print(f"   ✅ {key}: {value}")
        
        return True
    except Exception as e:
        print(f"   ❌ Error generating headers: {e}")
        return False


def suggest_configuration():
    """Suggest proper configuration based on findings."""
    print("\n=== CONFIGURATION SUGGESTIONS ===")
    
    print("For API token authentication (recommended), add to your .env file:")
    print("")
    print("   ATLASSIAN_AUTH_METHOD=token")
    print("   JIRA_BASE_URL=https://yourcompany.atlassian.net")
    print("   CONFLUENCE_BASE_URL=https://yourcompany.atlassian.net/wiki") 
    print("   ATLASSIAN_API_TOKEN=your_api_token_here")
    print("   ATLASSIAN_EMAIL=your_email@company.com")
    print("")
    print("To generate an API token:")
    print("   1. Go to https://id.atlassian.com/manage-profile/security/api-tokens")
    print("   2. Click 'Create API token'")
    print("   3. Copy the token and add it to your .env file")
    print("   4. Use your Atlassian account email address")


async def test_api_call(auth_manager):
    """Test an actual API call to see the specific error."""
    print("\n=== API CALL TEST ===")
    
    if not auth_manager.jira_base_url:
        print("   ❌ No Jira URL configured - cannot test API call")
        return
    
    import httpx
    
    try:
        url = f"{auth_manager.jira_base_url}/rest/api/3/myself"
        print(f"   Testing API call to: {url}")
        
        async with httpx.AsyncClient() as client:
            response = await auth_manager.make_request(client, "GET", url)
            
            print(f"   ✅ Response status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Authentication successful!")
                print(f"   ✅ User: {data.get('displayName', 'Unknown')}")
                print(f"   ✅ Email: {data.get('emailAddress', 'Unknown')}")
            else:
                print(f"   ❌ Response: {response.text}")
                
    except Exception as e:
        print(f"   ❌ API call failed: {e}")


def main():
    """Run complete Atlassian authentication diagnosis."""
    print("🔍 ATLASSIAN AUTHENTICATION DIAGNOSIS")
    print("=====================================")
    
    # Check environment variables
    has_env_vars = check_environment_variables()
    
    # Check settings configuration  
    auth_manager = check_settings_config()
    
    # Test auth headers
    headers_ok = test_auth_headers(auth_manager)
    
    # Test API call
    import asyncio
    asyncio.run(test_api_call(auth_manager))
    
    # Provide suggestions
    suggest_configuration()
    
    print(f"\n📋 DIAGNOSIS SUMMARY:")
    print(f"   Environment vars: {'✅ Found' if has_env_vars else '❌ Missing'}")
    print(f"   Auth headers: {'✅ Valid' if headers_ok else '❌ Invalid'}")
    
    if not has_env_vars:
        print(f"\n⚠️  Main issue: Missing environment variables in .env file")
        print(f"   Add the configuration shown above to fix 403 errors")


if __name__ == "__main__":
    main()