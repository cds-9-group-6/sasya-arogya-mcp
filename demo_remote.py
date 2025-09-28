#!/usr/bin/env python3
"""
Demo script for the remote MCP HTTP server
Shows how to use the server from any HTTP client
"""

import requests
import json


def demo_remote_mcp():
    """Demonstrate remote MCP server usage with simple HTTP requests"""
    
    base_url = "http://localhost:8001"
    
    print("🚀 Sasya Arogya MCP Server Demo")
    print("=" * 50)
    
    # 1. Health check
    print("\n1. Health Check:")
    response = requests.get(f"{base_url}/health")
    print(f"   Status: {response.json()['status']}")
    
    # 2. List tools
    print("\n2. Available Tools:")
    response = requests.get(f"{base_url}/tools")
    tools = response.json()['tools']
    for tool in tools:
        print(f"   • {tool['name']}")
    
    # 3. Calculate premium
    print("\n3. Calculate Crop Premium:")
    response = requests.post(f"{base_url}/tools/call", json={
        "name": "calculate_crop_premium",
        "arguments": {
            "crop": "Wheat",
            "area_hectare": 2.0,
            "state": "Punjab"
        }
    })
    result = response.json()
    print(f"   Result: {result['content'][0]['text'][:100]}...")
    
    # 4. Get insurance companies
    print("\n4. Get Insurance Companies:")
    response = requests.post(f"{base_url}/tools/call", json={
        "name": "get_insurance_companies",
        "arguments": {
            "state": "Punjab"
        }
    })
    result = response.json()
    print(f"   Found {len(result['content'][0]['text'].split('•')) - 1} companies")
    
    # 5. Test streaming
    print("\n5. Streaming Response:")
    response = requests.post(f"{base_url}/tools/call/stream", json={
        "name": "calculate_crop_premium",
        "arguments": {
            "crop": "Rice",
            "area_hectare": 1.5,
            "state": "West Bengal"
        }
    }, stream=True)
    
    print("   Streaming data:")
    for line in response.iter_lines():
        if line and line.startswith(b'data: '):
            data = json.loads(line[6:])
            if data.get('type') == 'content':
                print(f"     📊 {data['content']['text'][:50]}...")
            elif data.get('type') == 'complete':
                print("     ✅ Stream completed")
    
    print("\n🎉 Demo completed successfully!")
    print(f"🌐 Server running at: {base_url}")
    print(f"📖 API docs: {base_url}/docs")


if __name__ == "__main__":
    try:
        demo_remote_mcp()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to MCP server")
        print("   Make sure the server is running on port 8001")
        print("   Start it with: python3 mcp_http_server.py --port 8001")
    except Exception as e:
        print(f"❌ Error: {e}")
