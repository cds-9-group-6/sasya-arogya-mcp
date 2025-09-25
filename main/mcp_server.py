"""
MCP Agent Server for providing insurance.
"""
from fastapi import FastAPI, Query
from .services.insurance_advisor import recommend_insurance
import uvicorn

class MCPServer:
    def __init__(self):
        self.app = FastAPI(title="Plant Insurance MCP Server")
        self.configure_routes()

    def configure_routes(self):
        @self.app.get("/insurance/")
        def get_insurance(disease: str = Query(..., description="Name of the plant disease")):
            insurance_options = recommend_insurance(disease)
            return {
                "disease": disease,
                "insurance_options": insurance_options
            }

    def run(self):
        uvicorn.run(self.app, host="127.0.0.1", port=8000)
