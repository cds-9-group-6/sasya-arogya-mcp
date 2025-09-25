def recommend_insurance(disease_name):
    insurance_db = {
        "Powdery Mildew": [
            {"provider": "AgriShield", "coverage": "₹50,000", "premium": "₹500/year"},
            {"provider": "CropCare", "coverage": "₹75,000", "premium": "₹650/year"}
        ],
        "Leaf Spot": [
            {"provider": "FarmSecure", "coverage": "₹40,000", "premium": "₹400/year"}
        ],
        "Rust": [
            {"provider": "GreenGuard", "coverage": "₹60,000", "premium": "₹550/year"}
        ]
    }

    return insurance_db.get(disease_name, [
        {"provider": "General AgriPlan", "coverage": "₹30,000", "premium": "₹300/year"}
    ])
