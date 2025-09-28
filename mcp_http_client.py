"""
HTTP-based MCP Client for testing remote Sasya Arogya MCP Server
"""

import asyncio
import aiohttp
import json
from typing import Dict, Any, List


class MCPHTTPClient:
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url.rstrip("/")
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def health_check(self) -> Dict[str, Any]:
        """Check if the server is healthy"""
        async with self.session.get(f"{self.base_url}/health") as response:
            return await response.json()
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """List available tools"""
        async with self.session.get(f"{self.base_url}/tools") as response:
            data = await response.json()
            return data.get("tools", [])
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool synchronously"""
        payload = {
            "name": name,
            "arguments": arguments
        }
        
        async with self.session.post(
            f"{self.base_url}/tools/call",
            json=payload
        ) as response:
            return await response.json()
    
    async def call_tool_stream(self, name: str, arguments: Dict[str, Any]):
        """Call a tool with streaming response"""
        payload = {
            "name": name,
            "arguments": arguments
        }
        
        async with self.session.post(
            f"{self.base_url}/tools/call/stream",
            json=payload
        ) as response:
            async for line in response.content:
                if line:
                    line_str = line.decode('utf-8').strip()
                    if line_str.startswith('data: '):
                        try:
                            data = json.loads(line_str[6:])  # Remove 'data: ' prefix
                            yield data
                        except json.JSONDecodeError:
                            continue


async def test_remote_mcp_server():
    """Test the remote MCP server with various tool calls"""
    
    async with MCPHTTPClient("http://localhost:8001") as client:
        print("🔗 Connecting to Sasya Arogya MCP HTTP Server")
        print("=" * 60)
        
        # Health check
        print("\n🏥 Health Check:")
        health = await client.health_check()
        print(f"  Status: {health.get('status', 'unknown')}")
        print(f"  Timestamp: {health.get('timestamp', 'unknown')}")
        
        # List available tools
        print("\n📋 Available Tools:")
        tools = await client.list_tools()
        for tool in tools:
            print(f"  • {tool['name']}: {tool['description']}")
        
        print("\n" + "=" * 60)
        
        # Test 1: Calculate crop premium
        print("\n🧮 Testing calculate_crop_premium...")
        premium_result = await client.call_tool(
            "calculate_crop_premium",
            {
                "crop": "Wheat",
                "area_hectare": 2.5,
                "state": "Karnataka"
            }
        )
        print("Result:")
        for content in premium_result.get("content", []):
            if content.get("type") == "text":
                print(f"  {content['text']}")
        
        # Test 2: Get insurance companies
        print("\n🏢 Testing get_insurance_companies...")
        companies_result = await client.call_tool(
            "get_insurance_companies",
            {"state": "Karnataka"}
        )
        print("Result:")
        for content in companies_result.get("content", []):
            if content.get("type") == "text":
                print(f"  {content['text']}")
        
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
        
        cert_result = await client.call_tool(
            "generate_insurance_certificate",
            certificate_data
        )
        print("Result:")
        for content in cert_result.get("content", []):
            if content.get("type") == "text":
                print(f"  {content['text']}")
            elif content.get("type") == "resource":
                print(f"  PDF generated: {content['uri'][:50]}...")
        
        # Test 4: Streaming response
        print("\n🌊 Testing streaming response...")
        print("Streaming calculate_crop_premium:")
        async for data in client.call_tool_stream(
            "calculate_crop_premium",
            {
                "crop": "Rice",
                "area_hectare": 3.0,
                "state": "Tamil Nadu"
            }
        ):
            if data.get("type") == "content":
                content = data.get("content", {})
                if content.get("type") == "text":
                    print(f"  Stream: {content['text'][:100]}...")
            elif data.get("type") == "complete":
                print("  ✅ Streaming completed")
            elif data.get("type") == "error":
                print(f"  ❌ Error: {data.get('message')}")
        
        print("\n✅ All tests completed successfully!")


async def main():
    """Main entry point"""
    try:
        await test_remote_mcp_server()
    except Exception as e:
        print(f"❌ Error testing remote MCP server: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
