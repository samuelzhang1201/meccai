#!/usr/bin/env python3
"""
Direct test of Tableau usage workflow through tableau admin agent.
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from meccaai.apps.lumos_bedrock_agents import LumosBedrockAgentSystem
from meccaai.core.types import Message


async def test_tableau_usage_direct():
    """Test tableau admin agent directly for workbook usage."""
    print("=== DIRECT TABLEAU USAGE TEST ===")
    
    system = LumosBedrockAgentSystem()
    
    # Direct question to tableau admin
    message = "Get all workbooks first, then get content usage statistics for workbooks with less than 100 views. Show workbook names, IDs, owners, and view counts."
    messages = [Message(role="user", content=message)]
    
    print(f"📝 Direct message to Tableau Admin: '{message}'")
    
    try:
        # Call tableau_admin directly
        result = await system.process_request(messages, agent="tableau_admin")
        
        print(f"✅ Tableau Admin Response:")
        print(f"   Length: {len(result.content)} characters")
        
        if "API Error Response" in result.content:
            print(f"❌ Still getting API error - workflow not working properly")
        elif "content_items\": []" in result.content:
            print(f"❌ Empty content items - get_content_usage called incorrectly")
        else:
            print(f"🎯 Response looks good:")
            
        # Show first 500 characters of response
        response_preview = result.content[:500]
        print(f"\nResponse preview:\n{response_preview}...")
        
    except Exception as e:
        print(f"❌ Direct test failed: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Run the direct test."""
    print("🧪 Testing Tableau Admin directly...")
    asyncio.run(test_tableau_usage_direct())
    print("\n🔚 Direct test completed!")


if __name__ == "__main__":
    main()