def fetch_vendors(request, disease=None, medicine=None):
    # Logic to map disease to medicine, then fetch vendors
    # Return list of vendor dicts
    return {
        "query": {"disease": disease, "medicine": medicine},
        "vendors": [
            {"name": "AgroCare", "location": "Pune", "price": 120},
            {"name": "GreenGrow", "location": "Nashik", "price": 115}
        ]
    }

def purchase_medicine(request, vendor_name, medicine, quantity, buyer_name, location):
    # Logic to record purchase or simulate transaction
    return {
        "status": "success",
        "message": f"{quantity} units of {medicine} purchased from {vendor_name} by {buyer_name} in {location}."
    } 