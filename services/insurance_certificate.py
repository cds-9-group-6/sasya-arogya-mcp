import base64
import os
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT

from fastapi import Request
from fastapi.responses import StreamingResponse
from fastapi.templating import Jinja2Templates


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
        # Create PDF using reportlab
        pdf_stream = BytesIO()
        doc = SimpleDocTemplate(pdf_stream, pagesize=A4, 
                              rightMargin=1.5*cm, leftMargin=1.5*cm, 
                              topMargin=1.5*cm, bottomMargin=1.5*cm)
        
        # Get styles
        styles = getSampleStyleSheet()
        
        # Create custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=12,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#0056b3')
        )
        
        header_style = ParagraphStyle(
            'CustomHeader',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=6,
            alignment=TA_CENTER,
            textColor=colors.black
        )
        
        # Build PDF content
        story = []
        
        # Logo and header
        logo_data = get_logo_for_certificate()
        if logo_data:
            try:
                logo_img = Image(BytesIO(base64.b64decode(logo_data)), width=60, height=60)
                logo_img.hAlign = 'CENTER'
                story.append(logo_img)
                story.append(Spacer(1, 12))
            except Exception as e:
                print(f"Error adding logo: {e}")
        
        # Main title
        story.append(Paragraph("GOVERNMENT OF INDIA", header_style))
        story.append(Paragraph(f"Pradhan Mantri Fasal Bima Yojana - {certificate_data.get('policy_id', '').split('-')[1] if '-' in certificate_data.get('policy_id', '') else ''}", title_style))
        story.append(Spacer(1, 20))
        
        # Policy details table
        policy_data = [
            ['Policy ID:', certificate_data.get('policy_id', '')],
            ['Farmer Name:', certificate_data.get('farmer_name', '')],
            ['Farmer ID:', certificate_data.get('farmer_id', '')],
            ['Insurance Company:', f"{certificate_data.get('insurance_company_name', '')}, {certificate_data.get('company_address', '')}"]
        ]
        
        policy_table = Table(policy_data, colWidths=[3*cm, 8*cm])
        policy_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ]))
        story.append(policy_table)
        story.append(Spacer(1, 20))
        
        # Insurance Overview section
        story.append(Paragraph("Insurance Overview", styles['Heading2']))
        story.append(Spacer(1, 10))
        
        overview_data = [
            ['Sum Insured (Rs)/Hectare', 'Farmer Share (%)', 'Actuarial Rate (%)', 'Cut Off Date'],
            [f"{certificate_data.get('sum_insured_per_hectare', 0):.2f}", 
             f"{certificate_data.get('farmer_share_percent', 0):.2f}",
             f"{certificate_data.get('actuarial_rate_percent', 0):.2f}",
             certificate_data.get('cut_off_date', '')]
        ]
        
        overview_table = Table(overview_data, colWidths=[3*cm, 3*cm, 3*cm, 3*cm])
        overview_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(overview_table)
        story.append(Spacer(1, 20))
        
        # Crop & Premium Details section
        story.append(Paragraph("Crop & Premium Details", styles['Heading2']))
        story.append(Spacer(1, 10))
        
        crop_details = certificate_data.get('crop_details', {})
        crop_data = [
            ['Crop', 'Area (Hectare)', 'Premium Paid By Farmer (Rs)', 'Premium Paid By Govt (Rs)', 'Total Sum Insured (Rs)'],
            [crop_details.get('name', ''),
             f"{crop_details.get('area_hectare', 0):.1f}",
             f"{crop_details.get('premium_paid_by_farmer', 0):.2f}",
             f"{crop_details.get('premium_paid_by_govt', 0):.2f}",
             f"{crop_details.get('total_sum_insured', 0):.2f}"]
        ]
        
        crop_table = Table(crop_data, colWidths=[2.5*cm, 2.5*cm, 3*cm, 3*cm, 3*cm])
        crop_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(crop_table)
        story.append(Spacer(1, 20))
        
        # Terms and Conditions
        story.append(Paragraph("Terms & Conditions", styles['Heading2']))
        story.append(Spacer(1, 10))
        
        terms = certificate_data.get('terms_and_conditions', [])
        for i, term in enumerate(terms, 1):
            story.append(Paragraph(f"{i}. {term}", styles['Normal']))
            story.append(Spacer(1, 3))
        
        # Footer
        story.append(Spacer(1, 30))
        story.append(Paragraph("This is a computer-generated certificate and does not require a signature.", 
                              ParagraphStyle('Footer', parent=styles['Normal'], fontSize=9, 
                                           alignment=TA_CENTER, textColor=colors.grey)))
        
        # Build PDF
        doc.build(story)
        
        # Ensure the stream is at the beginning and get the content
        pdf_stream.seek(0)
        pdf_content = pdf_stream.getvalue()
        
        # Verify that we have content
        if not pdf_content:
            raise Exception("PDF generation failed - no content generated")
        
        # Close the original stream
        pdf_stream.close()

        name = certificate_data.get("farmer_name", "certificate")
        
        # Create a new BytesIO stream with the PDF content
        response_stream = BytesIO(pdf_content)
        
        return StreamingResponse(
            response_stream,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"inline; filename={name}_report.pdf",
                "Content-Length": str(len(pdf_content))
            },
        )

    except Exception as e:
        return f"An internal server error occurred: {str(e)}", 500
