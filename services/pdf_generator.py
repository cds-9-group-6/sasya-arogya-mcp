from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm


def create_pdf_from_html(html_content: str):
    """
    Converts a given HTML string into a PDF file in memory.
    Note: This is a simplified version that creates a basic PDF from HTML content.

    Args:
        html_content: A string containing the fully rendered HTML.

    Returns:
        The raw bytes of the generated PDF, or None if an error occurred.
    """
    try:
        # Create PDF using reportlab
        pdf_buffer = BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=A4, 
                              rightMargin=1.5*cm, leftMargin=1.5*cm, 
                              topMargin=1.5*cm, bottomMargin=1.5*cm)
        
        # Get styles
        styles = getSampleStyleSheet()
        
        # Build PDF content
        story = []
        
        # Add a simple paragraph with the HTML content
        # This is a basic implementation - for complex HTML, you'd need HTML parsing
        story.append(Paragraph("Document Content", styles['Heading1']))
        story.append(Spacer(1, 12))
        
        # Simple text extraction from HTML (basic implementation)
        import re
        # Remove HTML tags for basic text extraction
        text_content = re.sub(r'<[^>]+>', '', html_content)
        # Split into lines and create paragraphs
        lines = text_content.split('\n')
        for line in lines:
            line = line.strip()
            if line:
                story.append(Paragraph(line, styles['Normal']))
                story.append(Spacer(1, 6))
        
        # Build PDF
        doc.build(story)
        pdf_buffer.seek(0)
        
        return pdf_buffer.getvalue()

    except Exception as e:
        print(f"An unexpected error occurred in PDF generation: {e}")
        return None
