"""
MCP Client for testing Sasya Arogya MCP Server
"""

import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def test_mcp_server():
    """Test the MCP server with various tool calls"""
    
    # Server parameters
    server_params = StdioServerParameters(
        command="python3",
        args=["mcp_server_simple.py"]
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the session
            await session.initialize()
            
            print("🔗 Connected to Sasya Arogya MCP Server")
            print("=" * 50)
            
            # List available tools
            print("\n📋 Available Tools:")
            tools_result = await session.list_tools()
            for tool in tools_result.tools:
                print(f"  • {tool.name}: {tool.description}")
            
            print("\n" + "=" * 50)
            
            # Test 1: Calculate crop premium
            print("\n🧮 Testing calculate_crop_premium...")
            premium_result = await session.call_tool(
                "calculate_crop_premium",
                {
                    "crop": "Wheat",
                    "area_hectare": 2.5,
                    "state": "Karnataka"
                }
            )
            print("Result:")
            for content in premium_result.content:
                if hasattr(content, 'text'):
                    print(f"  {content.text}")
            
            # Test 2: Get insurance companies
            print("\n🏢 Testing get_insurance_companies...")
            companies_result = await session.call_tool(
                "get_insurance_companies",
                {"state": "Karnataka"}
            )
            print("Result:")
            for content in companies_result.content:
                if hasattr(content, 'text'):
                    print(f"  {content.text}")
            
            # Test 3: Generate insurance certificate
            print("\n📄 Testing generate_insurance_certificate...")
            certificate_data = {
                "policy_id": "PMFBY-2024-001",
                "farmer_name": "Ramesh Kumar",
                "farmer_id": "F12345",
                "insurance_company_name": "ABC Insurance Ltd",
                "company_address": "123 Main St, Bangalore",
                "sum_insured_per_hectare": 50000.0,
                "farmer_share_percent": 2.0,
                "actuarial_rate_percent": 3.5,
                "cut_off_date": "2024-12-31",
                "crop_details": {
                    "name": "Wheat",
                    "area_hectare": 2.5,
                    "premium_paid_by_farmer": 2500.0,
                    "premium_paid_by_govt": 7500.0,
                    "total_sum_insured": 125000.0
                },
                "terms_and_conditions": [
                    "This policy covers natural calamities and pest attacks",
                    "Claims must be filed within 15 days of damage",
                    "Assessment will be done by authorized personnel",
                    "Payment will be made within 30 days of claim approval"
                ]
            }
            
            cert_result = await session.call_tool(
                "generate_insurance_certificate",
                certificate_data
            )
            print("Result:")
            for content in cert_result.content:
                if hasattr(content, 'text'):
                    print(f"  {content.text}")
                elif hasattr(content, 'uri'):
                    print(f"  PDF generated: {content.uri[:50]}...")
            
            print("\n✅ All tests completed successfully!")


async def main():
    """Main entry point"""
    try:
        await test_mcp_server()
    except Exception as e:
        print(f"❌ Error testing MCP server: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
