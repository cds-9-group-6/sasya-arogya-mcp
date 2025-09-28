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
                description="Generate an insurance certificate PDF for a farmer",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "policy_id": {"type": "string", "description": "Unique policy identifier"},
                        "farmer_name": {"type": "string", "description": "Name of the farmer"},
                        "farmer_id": {"type": "string", "description": "Farmer identification number"},
                        "insurance_company_name": {"type": "string", "description": "Name of the insurance company"},
                        "company_address": {"type": "string", "description": "Address of the insurance company"},
                        "sum_insured_per_hectare": {"type": "number", "description": "Sum insured per hectare in rupees"},
                        "farmer_share_percent": {"type": "number", "description": "Farmer's share percentage"},
                        "actuarial_rate_percent": {"type": "number", "description": "Actuarial rate percentage"},
                        "cut_off_date": {"type": "string", "description": "Cut-off date for the policy"},
                        "crop_details": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "area_hectare": {"type": "number"},
                                "premium_paid_by_farmer": {"type": "number"},
                                "premium_paid_by_govt": {"type": "number"},
                                "total_sum_insured": {"type": "number"}
                            }
                        },
                        "terms_and_conditions": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of terms and conditions"
                        }
                    },
                    "required": ["policy_id", "farmer_name", "farmer_id", "insurance_company_name", "company_address", "sum_insured_per_hectare", "farmer_share_percent", "actuarial_rate_percent", "cut_off_date", "crop_details", "terms_and_conditions"]
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
                
                result = generate_certificate(MockRequest(), arguments)
                
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
