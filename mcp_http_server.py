"""
HTTP-based MCP Server for Sasya Arogya - Insurance and Crop Management
Supports both stdio and HTTP modes for remote access and containerization
"""

import asyncio
import base64
import json
from typing import Any, Dict, List

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from services.crop_premium import calculate_premium
from services.insurance_advisor import recommend_insurance
from services.insurance_certificate import generate_certificate
from services.insurance_companies import get_insurance_companies


# Pydantic models for request/response
class ToolCallRequest(BaseModel):
    name: str
    arguments: Dict[str, Any]


class ToolCallResponse(BaseModel):
    content: List[Dict[str, Any]]
    isError: bool = False


class ListToolsResponse(BaseModel):
    tools: List[Dict[str, Any]]


# Create FastAPI app
app = FastAPI(
    title="Sasya Arogya MCP Server",
    description="MCP Server for Insurance and Crop Management",
    version="1.0.0"
)

# Add CORS middleware for remote access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Available tools definition
MCP_TOOLS = [
    {
        "name": "calculate_crop_premium",
        "description": "Calculate insurance premium for a specific crop and area",
        "inputSchema": {
            "type": "object",
            "properties": {
                "crop": {"type": "string", "description": "Name of the crop"},
                "area_hectare": {"type": "number", "description": "Area in hectares"},
                "state": {"type": "string", "description": "State where the crop is grown"}
            },
            "required": ["crop", "area_hectare", "state"]
        }
    },
    {
        "name": "get_insurance_companies",
        "description": "Get list of available insurance companies",
        "inputSchema": {
            "type": "object",
            "properties": {
                "state": {"type": "string", "description": "State to filter companies (optional)"}
            }
        }
    },
    {
        "name": "generate_insurance_certificate",
        "description": "Generate an insurance certificate PDF for a farmer",
        "inputSchema": {
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
    },
    {
        "name": "recommend_insurance",
        "description": "Recommend insurance for a farmer based on crop, disease, and location",
        "inputSchema": {
            "type": "object",
            "properties": {
                "disease": {"type": "string", "description": "Name of the plant disease affecting the crop"},
                "farmer_name": {"type": "string", "description": "Name of the farmer"},
                "state": {"type": "string", "description": "State where the farmer is located"},
                "area_hectare": {"type": "number", "description": "Area of cultivation in hectares"},
                "crop": {"type": "string", "description": "Name of the crop being cultivated"}
            },
            "required": ["disease", "farmer_name", "state", "area_hectare", "crop"]
        }
    }
]


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Sasya Arogya MCP Server",
        "version": "1.0.0",
        "status": "running",
        "tools": len(MCP_TOOLS)
    }


@app.get("/tools", response_model=ListToolsResponse)
async def list_tools():
    """List available MCP tools"""
    return ListToolsResponse(tools=MCP_TOOLS)


@app.post("/tools/call", response_model=ToolCallResponse)
async def call_tool(request: ToolCallRequest):
    """Call an MCP tool"""
    try:
        result = await execute_tool(request.name, request.arguments)
        return ToolCallResponse(content=result, isError=False)
    except Exception as e:
        return ToolCallResponse(
            content=[{"type": "text", "text": f"Error executing tool {request.name}: {str(e)}"}],
            isError=True
        )


@app.post("/tools/call/stream")
async def call_tool_stream(request: ToolCallRequest):
    """Call an MCP tool with streaming response"""
    try:
        async def generate_response():
            yield f"data: {json.dumps({'type': 'start', 'tool': request.name})}\n\n"
            
            try:
                result = await execute_tool(request.name, request.arguments)
                
                # Stream each content item
                for i, content in enumerate(result):
                    yield f"data: {json.dumps({'type': 'content', 'index': i, 'content': content})}\n\n"
                    await asyncio.sleep(0.1)  # Small delay for streaming effect
                
                yield f"data: {json.dumps({'type': 'complete'})}\n\n"
                
            except Exception as e:
                yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
        
        return StreamingResponse(
            generate_response(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/event-stream"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def execute_tool(name: str, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Execute the specified tool with given arguments"""
    
    if name == "calculate_crop_premium":
        premium_data = calculate_premium(
            arguments["crop"],
            arguments["area_hectare"],
            arguments["state"]
        )
        
        return [{
            "type": "text",
            "text": f"Premium calculation for {arguments['crop']} in {arguments['state']}:\n" +
                   f"Area: {arguments['area_hectare']} hectares\n" +
                   f"Premium per hectare: ₹{premium_data.get('premium_per_hectare', 0):.2f}\n" +
                   f"Total premium: ₹{premium_data.get('total_premium', 0):.2f}\n" +
                   f"Government subsidy: ₹{premium_data.get('govt_subsidy', 0):.2f}\n" +
                   f"Farmer contribution: ₹{premium_data.get('farmer_contribution', 0):.2f}"
        }]
    
    elif name == "get_insurance_companies":
        companies = get_insurance_companies(arguments.get("state"))
        
        company_list = "\n".join([
            f"• {company['name']} - {company['address']}" 
            for company in companies
        ])
        
        return [{
            "type": "text",
            "text": f"Available insurance companies{' in ' + arguments['state'] if arguments.get('state') else ''}:\n{company_list}"
        }]
    
    elif name == "generate_insurance_certificate":
        # Create a mock request object
        class MockRequest:
            pass
        
        result = generate_certificate(MockRequest(), arguments)
        
        if hasattr(result, 'body'):
            # If it's a StreamingResponse, extract the PDF data
            pdf_data = b"".join(result.body)
            pdf_base64 = base64.b64encode(pdf_data).decode('utf-8')
            
            return [
                {
                    "type": "text",
                    "text": f"Insurance certificate generated successfully. PDF size: {len(pdf_data)} bytes"
                },
                {
                    "type": "resource",
                    "uri": f"data:application/pdf;base64,{pdf_base64}",
                    "mimeType": "application/pdf",
                    "text": "Insurance Certificate PDF"
                }
            ]
        else:
            return [{"type": "text", "text": str(result)}]
    
    elif name == "recommend_insurance":
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
            pdf_base64 = base64.b64encode(pdf_data).decode('utf-8')
            
            return [
                {
                    "type": "text",
                    "text": f"Insurance recommendation generated successfully. PDF size: {len(pdf_data)} bytes"
                },
                {
                    "type": "resource",
                    "uri": f"data:application/pdf;base64,{pdf_base64}",
                    "mimeType": "application/pdf",
                    "text": "Insurance Recommendation PDF"
                }
            ]
        else:
            return [{"type": "text", "text": str(result)}]
    
    else:
        return [{"type": "text", "text": f"Unknown tool: {name}"}]


@app.get("/health")
async def health_check():
    """Health check endpoint for container orchestration"""
    return {"status": "healthy", "timestamp": asyncio.get_event_loop().time()}


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Sasya Arogya MCP HTTP Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    
    args = parser.parse_args()
    
    print(f"🚀 Starting Sasya Arogya MCP HTTP Server on {args.host}:{args.port}")
    print(f"📋 Available tools: {len(MCP_TOOLS)}")
    print(f"🌐 Health check: http://{args.host}:{args.port}/health")
    print(f"📖 API docs: http://{args.host}:{args.port}/docs")
    
    uvicorn.run(
        "mcp_http_server:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level="info"
    )
