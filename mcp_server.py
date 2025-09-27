"""
MCP Agent Server for providing insurance.
"""

from fastapi import FastAPI, Query, Request
from services.insurance_advisor import recommend_insurance
from vendor.vendor_advisor import fetch_vendors, purchase_medicine
import uvicorn


class MCPServer:
    def __init__(self):
        self.app = FastAPI(title="Sasya Arogya MCP Server")
        self.configure_routes()

    # Request,disease,name,state,area_hectare,crop
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

        @self.app.get("/vendors/")
        def get_vendors(
            request: Request,
            disease: str = Query(None),
            medicine: str = Query(None),
        ):
            """
            Fetch vendors based on disease or medicine.
            Either 'disease' or 'medicine' must be provided.
            """
            return fetch_vendors(request,disease=disease, medicine=medicine)

        @self.app.post("/purchase/")
        def purchase(
            request: Request,
            vendor_name: str,
            medicine: str,
            quantity: int,
            buyer_name: str,
            location: str,
        ):
            """
            Perform medicine purchase from a vendor.
            """
            return purchase_medicine(
                request,
                vendor_name=vendor_name,
                medicine=medicine,
                quantity=quantity,
                buyer_name=buyer_name,
                location=location,
            )
            


    def run(self):
        uvicorn.run(self.app, host="127.0.0.1", port=8000)


def run_server():
    # Configure and start the MCP server
    server = MCPServer()
    server.run()


if __name__ == "__main__":
    run_server()
