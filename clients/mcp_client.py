import requests


class MultiServerMCPClient:
    def __init__(self, base_url: str):
        """
        Initialize the client with the base URL of the MCP server.

        :param base_url: The base URL of the MCP server (e.g., "http://127.0.0.1:8000")
        """
        self.base_url = base_url.rstrip("/")

    def get_insurance_pdf(
        self,
        disease: str,
        name: str,
        state: str,
        area_hectare: float,
        crop: str,
        output_file: str,
    ):
        """
        Call the /insurance/ endpoint to get the insurance certificate as a PDF.

        :param disease: Name of the plant disease
        :param name: Name of the farmer
        :param state: State of the farmer
        :param area_hectare: Area in hectares
        :param crop: Name of the crop
        :param output_file: Path to save the PDF file
        :return: True if the PDF is successfully saved, False otherwise
        """
        endpoint = f"{self.base_url}/insurance/"
        params = {
            "disease": disease,
            "name": name,
            "state": state,
            "area_hectare": area_hectare,
            "crop": crop,
        }

        try:
            response = requests.get(endpoint, params=params, stream=True)
            response.raise_for_status()  # Raise an exception for HTTP errors

            # Check if the response is a PDF
            if response.headers.get("Content-Type") == "application/pdf":
                # Save the PDF to the specified file
                with open(output_file, "wb") as pdf_file:
                    for chunk in response.iter_content(chunk_size=8192):
                        pdf_file.write(chunk)
                print(f"PDF successfully saved to {output_file}")
                return True
            else:
                print("Unexpected content type:", response.headers.get("Content-Type"))
                return False

        except requests.exceptions.RequestException as e:
            print(f"Error while calling MCP server: {e}")
            return False


if __name__ == "__main__":
    # Example usage of the MultiServerMCPClient
    client = MultiServerMCPClient(base_url="http://127.0.0.1:8000")

    # Example parameters
    disease = "Powdery Mildew"
    name = "Ramesh"
    state = "Karnataka"
    area_hectare = 5.0
    crop = "Wheat"
    output_file = "insurance_certificate.pdf"

    # Call the /insurance/ endpoint and save the PDF
    success = client.get_insurance_pdf(
        disease, name, state, area_hectare, crop, output_file
    )
    if success:
        print("Insurance certificate downloaded successfully.")
    else:
        print("Failed to download the insurance certificate.")
