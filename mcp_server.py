"""
MCP Agent Server for providing insurance.
"""

from fastapi import FastAPI, Query, Request
from services.insurance_advisor import recommend_insurance
import uvicorn


class MCPServer:
    def __init__(self):
        self.app = FastAPI(title="Plant Insurance MCP Server")
        self.configure_routes()

    # disease,name,state,area_hectare,crop
    def configure_routes(self):
        @self.app.get("/insurance/")
        def get_insurance(
            request: Request,
            disease: str,
            name: str,
            state: str,
            area_hectare: float,
            crop: str,
        ):
            # Pass the query parameters to the recommend_insurance function
            # return recommend_insurance(disease, name, state, area_hectare, crop)
            return recommend_insurance(
                request, disease, name, state, area_hectare, crop
            )

    def run(self):
        uvicorn.run(self.app, host="127.0.0.1", port=8000)
