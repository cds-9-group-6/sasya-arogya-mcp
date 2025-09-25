from io import BytesIO
from xhtml2pdf import pisa


def create_pdf_from_html(html_content: str):
    """
    Converts a given HTML string into a PDF file in memory.

    Args:
        html_content: A string containing the fully rendered HTML.

    Returns:
        The raw bytes of the generated PDF, or None if an error occurred.
    """
    try:
        # Create a BytesIO buffer to hold the PDF data in memory
        pdf_buffer = BytesIO()

        # Create the PDF document
        pisa_status = pisa.CreatePDF(
            BytesIO(html_content.encode("UTF-8")),  # The source HTML string
            dest=pdf_buffer,  # The destination buffer
        )

        # If there was an error during creation, return None
        if pisa_status.err:
            print(f"Error creating PDF: {pisa_status.err}")
            return None

        # Go to the beginning of the buffer and get its content
        pdf_buffer.seek(0)
        pdf_bytes = pdf_buffer.getvalue()

        return pdf_bytes

    except Exception as e:
        print(f"An unexpected error occurred in PDF generation: {e}")
        return None
