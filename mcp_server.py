"""
MCP Server for Sasya Arogya - Insurance and Crop Management
"""

import asyncio
import json
from typing import Any, Dict

from mcp.server import NotificationOptions
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolResult,
    ListToolsResult,
    Tool,
    TextContent,
    EmbeddedResource
)

from services.crop_premium import calculate_premium
from services.insurance_advisor import recommend_insurance, calculate_policy_details
from services.insurance_certificate import generate_certificate
from services.insurance_companies import get_insurance_companies


class SasyaArogyaMCPServer:
    def __init__(self):
        self.server = Server("sasya-arogya-mcp")
        self.setup_handlers()
    
    def setup_handlers(self):
        """Setup MCP server handlers for tools and resources"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> ListToolsResult:
            """List available tools for insurance and crop management"""
            tools = [
                Tool(
                    name="recommend_insurance",
                    description="Recommend insurance for a farmer based on crop, disease, and location",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "disease": {
                                "type": "string",
                                "description": "Name of the plant disease affecting the crop"
                            },
                            "farmer_name": {
                                "type": "string", 
                                "description": "Name of the farmer"
                            },
                            "state": {
                                "type": "string",
                                "description": "State where the farmer is located"
                            },
                            "area_hectare": {
                                "type": "number",
                                "description": "Area of cultivation in hectares"
                            },
                            "crop": {
                                "type": "string",
                                "description": "Name of the crop being cultivated"
                            }
                        },
                        "required": ["disease", "farmer_name", "state", "area_hectare", "crop"]
                    }
                ),
                Tool(
                    name="generate_insurance_certificate",
                    description="Generate an insurance certificate PDF for a farmer with automatic premium calculations",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "farmer_name": {
                                "type": "string",
                                "description": "Name of the farmer"
                            },
                            "state": {
                                "type": "string",
                                "description": "State where the farmer is located"
                            },
                            "area_hectare": {
                                "type": "number",
                                "description": "Area of cultivation in hectares"
                            },
                            "crop": {
                                "type": "string",
                                "description": "Name of the crop being cultivated"
                            },
                            "disease": {
                                "type": "string",
                                "description": "Name of the plant disease affecting the crop (optional)"
                            }
                        },
                        "required": ["farmer_name", "state", "area_hectare", "crop"]
                    }
                ),
                Tool(
                    name="calculate_crop_premium",
                    description="Calculate insurance premium for a specific crop and area",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "crop": {
                                "type": "string",
                                "description": "Name of the crop"
                            },
                            "area_hectare": {
                                "type": "number",
                                "description": "Area in hectares"
                            },
                            "state": {
                                "type": "string",
                                "description": "State where the crop is grown"
                            }
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
                            "state": {
                                "type": "string",
                                "description": "State to filter companies (optional)"
                            }
                        }
                    }
                )
            ]
            return ListToolsResult(tools=tools)
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
            """Handle tool calls"""
            try:
                if name == "recommend_insurance":
                    # Create a mock request object
                    class MockRequest:
                        pass
                    
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
                                    text=f"Insurance recommendation generated successfully. PDF size: {len(pdf_data)} bytes"
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
                
                elif name == "generate_insurance_certificate":
                    # Create a mock request object
                    class MockRequest:
                        pass
                    
                    # First calculate premium data for the text response
                    premium_data = calculate_premium(
                        arguments["crop"],
                        arguments["area_hectare"],
                        arguments["state"]
                    )
                    
                    # Use the insurance advisor to calculate all policy details and generate certificate
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
                        
                        # Get sum insured (already the total amount)
                        total_sum_insured = premium_data.get('sum_insured_per_hectare', 0)
                        
                        # Create detailed text response with premium calculations
                        premium_text = (
                            f"Insurance certificate generated successfully for {arguments['farmer_name']}!\n\n"
                            f"Premium calculation for {arguments['crop']} in {arguments['state']}:\n"
                            f"Area: {arguments['area_hectare']} hectares\n"
                            f"Sum insured: ₹{total_sum_insured:.2f}\n"
                            f"Premium per hectare: ₹{premium_data.get('premium_per_hectare', 0):.2f}\n"
                            f"Total premium: ₹{premium_data.get('total_premium', 0):.2f}\n"
                            f"Government subsidy: ₹{premium_data.get('govt_subsidy', 0):.2f}\n"
                            f"Farmer contribution: ₹{premium_data.get('farmer_contribution', 0):.2f}\n"
                            f"Insurance Company: {premium_data.get('insurance_company_name', 'N/A')}\n"
                            f"Company Address: {premium_data.get('company_address', 'N/A')}\n\n"
                            f"PDF certificate size: {len(pdf_data)} bytes"
                        )
                        
                        return CallToolResult(
                            content=[
                                TextContent(
                                    type="text",
                                    text=premium_text
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
                
                elif name == "calculate_crop_premium":
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
                                 f"Sum insured per hectare: ₹{premium_data.get('sum_insured_per_hectare', 0):.2f}\n" +
                                 f"Premium per hectare: ₹{premium_data.get('premium_per_hectare', 0):.2f}\n" +
                                 f"Total premium: ₹{premium_data.get('total_premium', 0):.2f}\n" +
                                 f"Government subsidy: ₹{premium_data.get('govt_subsidy', 0):.2f}\n" +
                                 f"Farmer contribution: ₹{premium_data.get('farmer_contribution', 0):.2f}\n" +
                                 f"Insurance Company: {premium_data.get('insurance_company_name', 'N/A')}\n" +
                                 f"Company Address: {premium_data.get('company_address', 'N/A')}"
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
                
                else:
                    return CallToolResult(
                        content=[TextContent(type="text", text=f"Unknown tool: {name}")]
                    )
                    
            except Exception as e:
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Error executing tool {name}: {str(e)}")]
                )
    
    async def run(self):
        """Run the MCP server"""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="sasya-arogya-mcp",
                    server_version="1.0.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={}
                    )
                )
            )


async def main():
    """Main entry point"""
    server = SasyaArogyaMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
