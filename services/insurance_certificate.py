import os
import base64
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.templating import Jinja2Templates
from xhtml2pdf import pisa
from io import BytesIO
import json


# Function to encode the logo image to Base64
def get_logo_for_certificate():
    """Reads the logo file and returns it as a Base64 encoded string."""
    try:
        logo_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "resources",
            "india_logo.jpg",
        )
        print(f"DEBUG: Attempting to read logo from {logo_path}")
        with open(logo_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
    except FileNotFoundError:
        print(f"ERROR: Logo file not found at {logo_path}")
        return None


def generate_certificate(request: Request, certificate_data: dict):
    try:
        templates = Jinja2Templates(directory="templates")

        logo_data = get_logo_for_certificate()
        print("DEBUG: Logo data successfully encoded to Base64.")

        # 1. Render the HTML template into a string
        # Render HTML from template
        html = templates.get_template("insurance_template.html").render(
            {"request": request, "data": certificate_data, "logo_data": logo_data}
        )

        print("DEBUG: HTML template successfully rendered.")
        print(f"Rendered HTML: {html[:500]}...")  # Print first 500 chars

        # Convert HTML to PDF
        pdf_stream = BytesIO()
        pisa.CreatePDF(html, dest=pdf_stream)
        pdf_stream.seek(0)

        name = certificate_data.get("farmer_name", "certificate")
        return StreamingResponse(
            pdf_stream,
            media_type="application/pdf",
            headers={"Content-Disposition": f"inline; filename={name}_report.pdf"},
        )

    except Exception as e:
        return f"An internal server error occurred: {str(e)}", 500
