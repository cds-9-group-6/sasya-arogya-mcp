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
                "farmer_name": "Ramesh Kumar",
                "state": "Karnataka",
                "area_hectare": 2.5,
                "crop": "Wheat",
                "disease": "Powdery Mildew"
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
