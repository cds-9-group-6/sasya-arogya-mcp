def generate_certificate_from_form():
    try:
        farmer_name = request.form.get("farmer_name")
        crop_name = request.form.get("crop_name")
        area_hectare = float(request.form.get("area_hectare"))
        if not all([farmer_name, crop_name, area_hectare]):
            return "Error: All fields are required.", 400

        certificate_data = calculate_policy_details(
            farmer_name, crop_name, area_hectare
        )
        logo_data = get_image_as_base64()

        # 1. Render the HTML template into a string
        rendered_html = render_template(
            "certificate_template.html", data=certificate_data, logo_data=logo_data
        )

        # 2. Use our new module to convert the HTML string to PDF bytes
        pdf_bytes = create_pdf_from_html(rendered_html)

        # 3. Check if PDF generation was successful
        if pdf_bytes is None:
            return "Error creating PDF.", 500

        # 4. Create the response
        response = make_response(pdf_bytes)
        response.headers["Content-Type"] = "application/pdf"
        response.headers["Content-Disposition"] = (
            f'inline; filename={certificate_data["policy_id"]}.pdf'
        )
        return response

    except Exception as e:
        return f"An internal server error occurred: {str(e)}", 500
