"""
Simple MCP Server for Sasya Arogya - Insurance and Crop Management
"""

import asyncio
import json
from typing import Any, Dict, List, Optional
from io import BytesIO

from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolResult,
    ListToolsResult,
    Tool,
    TextContent,
    EmbeddedResource
)

from services.insurance_advisor import recommend_insurance
from services.insurance_certificate import generate_certificate
from services.crop_premium import calculate_premium
from services.insurance_companies import get_insurance_companies


async def main():
    """Main entry point for the MCP server"""
    
    # Create server
    server = Server("sasya-arogya-mcp")
    
    @server.list_tools()
    async def handle_list_tools() -> ListToolsResult:
        """List available tools"""
        tools = [
            Tool(
                name="calculate_crop_premium",
                description="Calculate insurance premium for a specific crop and area",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "crop": {"type": "string", "description": "Name of the crop"},
                        "area_hectare": {"type": "number", "description": "Area in hectares"},
                        "state": {"type": "string", "description": "State where the crop is grown"}
                    },
                    "required": ["crop", "area_hectare", "state"]
                }
            ),
            Tool(
                name="get_insurance_companies",
                description="Get list of available insurance companies",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "state": {"type": "string", "description": "State to filter companies (optional)"}
                    }
                }
            ),
            Tool(
                name="generate_insurance_certificate",
                description="Generate an insurance certificate PDF for a farmer with automatic premium calculations",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "farmer_name": {"type": "string", "description": "Name of the farmer"},
                        "state": {"type": "string", "description": "State where the farmer is located"},
                        "area_hectare": {"type": "number", "description": "Area of cultivation in hectares"},
                        "crop": {"type": "string", "description": "Name of the crop being cultivated"},
                        "disease": {"type": "string", "description": "Name of the plant disease affecting the crop (optional)"}
                    },
                    "required": ["farmer_name", "state", "area_hectare", "crop"]
                }
            )
        ]
        return ListToolsResult(tools=tools)
    
    @server.call_tool()
    async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
        """Handle tool calls"""
        try:
            if name == "calculate_crop_premium":
                premium_data = calculate_premium(
                    arguments["crop"],
                    arguments["area_hectare"],
                    arguments["state"]
                )
                
                return CallToolResult(
                    content=[TextContent(
                        type="text",
                        text=f"Premium calculation for {arguments['crop']} in {arguments['state']}:\n" +
                             f"Area: {arguments['area_hectare']} hectares\n" +
                             f"Premium per hectare: ₹{premium_data.get('premium_per_hectare', 0):.2f}\n" +
                             f"Total premium: ₹{premium_data.get('total_premium', 0):.2f}\n" +
                             f"Government subsidy: ₹{premium_data.get('govt_subsidy', 0):.2f}\n" +
                             f"Farmer contribution: ₹{premium_data.get('farmer_contribution', 0):.2f}"
                    )]
                )
            
            elif name == "get_insurance_companies":
                companies = get_insurance_companies(arguments.get("state"))
                
                company_list = "\n".join([
                    f"• {company['name']} - {company['address']}" 
                    for company in companies
                ])
                
                return CallToolResult(
                    content=[TextContent(
                        type="text",
                        text=f"Available insurance companies{' in ' + arguments['state'] if arguments.get('state') else ''}:\n{company_list}"
                    )]
                )
            
            elif name == "generate_insurance_certificate":
                # Create a mock request object
                class MockRequest:
                    pass
                
                # Use the insurance advisor to calculate all policy details
                result = recommend_insurance(
                    MockRequest(),
                    arguments["farmer_name"],
                    arguments["state"],
                    arguments["area_hectare"],
                    arguments["crop"],
                    arguments.get("disease")  # Optional disease parameter
                )
                
                if hasattr(result, 'body'):
                    # If it's a StreamingResponse, extract the PDF data
                    pdf_data = b"".join(result.body)
                    return CallToolResult(
                        content=[
                            TextContent(
                                type="text",
                                text=f"Insurance certificate generated successfully. PDF size: {len(pdf_data)} bytes"
                            ),
                            EmbeddedResource(
                                uri="data:application/pdf;base64," + 
                                    json.dumps(pdf_data.decode('latin-1')),
                                mimeType="application/pdf",
                                text="Insurance Certificate PDF"
                            )
                        ]
                    )
                else:
                    return CallToolResult(
                        content=[TextContent(type="text", text=str(result))]
                    )
            
            else:
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Unknown tool: {name}")]
                )
                
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error executing tool {name}: {str(e)}")]
            )
    
    # Run the server
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="sasya-arogya-mcp",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )


if __name__ == "__main__":
    asyncio.run(main())
