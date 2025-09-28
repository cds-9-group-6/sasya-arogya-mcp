import random
from datetime import datetime, timedelta

from fastapi import Request

from services.crop_premium import get_crop_premium_data
# from services.insurance_certificate import generate_certificate
from services.insurance_certificate import generate_certificate
from services.insurance_companies import get_registered_insurers


def recommend_insurance(request: Request, disease, name, state, area_hectare, crop):
    policy_data = calculate_policy_details(name, state, area_hectare, crop)
    print(f"Generated Policy Data: {policy_data}")
    response = generate_certificate(request, policy_data)
    return response


def get_farmer_share_percent(crop_type):
    if crop_type == "Kharif":
        return 0.02
    elif crop_type == "Rabi":
        return 0.015
    elif crop_type == "Horticulture":
        return 0.05
    return 0.02


def calculate_policy_details(name, state, area_hectare, crop) -> dict:
    farmer_name = name
    crop_name = crop
    area_hectare = area_hectare
    crop_df = get_crop_premium_data()
    # Load insurance companies data and reset rates (randomize) for demo purposes
    companies_df = get_registered_insurers(reset_rates=True)

    if not all([farmer_name, crop_name, area_hectare]):
        raise ValueError("All fields are required.")
    if area_hectare <= 0:
        raise ValueError("Area must be a positive number.")

    crop_info = crop_df[crop_df["Crop"].str.lower() == crop_name.lower()]
    if crop_info.empty:
        raise ValueError(f"Crop '{crop_name}' not found.")
    crop_info = crop_info.iloc[0]

    scale_of_finance = crop_info["Scale of Finance (Rs/Hectare)"]
    actuarial_rate = crop_info["Actuarial Premium Rate (%)"] / 100

    farmer_share_percent = get_farmer_share_percent(crop_info["Season"])
    sum_insured = scale_of_finance * area_hectare
    premium_paid_by_farmer = sum_insured * farmer_share_percent

    # Find the insurance company offering the lowest gross premium
    best_company = None
    lowest_gross_premium = float("inf")
    for index, company in companies_df.iterrows():
        rate_multiplier = company["Rate_Multiplier"]
        company_gross_premium = sum_insured * actuarial_rate * rate_multiplier
        if company_gross_premium < lowest_gross_premium:
            lowest_gross_premium = company_gross_premium
            best_company = company

    if best_company is None:
        raise ValueError("No insurance companies available.")

    premium_paid_by_govt = lowest_gross_premium - premium_paid_by_farmer

    policy_id = f"PMFBY-{datetime.now().year}-AG{random.randint(1000, 9999)}K"
    farmer_id = f"FKID-{random.randint(100000000, 999999999)}"
    cut_off_date = (datetime.now() + timedelta(days=45)).strftime("%d-%m-%Y")

    policy_data = {
        "policy_id": policy_id,
        "farmer_name": farmer_name.title(),
        "farmer_id": farmer_id,
        "insurance_company_name": best_company["Company Name"],
        "company_address": best_company["Address"],
        "sum_insured_per_hectare": scale_of_finance,
        "farmer_share_percent": farmer_share_percent * 100,
        "actuarial_rate_percent": actuarial_rate * 100,
        "cut_off_date": cut_off_date,
        "crop_details": {
            "name": crop_info["Crop"],
            "area_hectare": area_hectare,
            "premium_paid_by_farmer": round(premium_paid_by_farmer, 2),
            "premium_paid_by_govt": round(premium_paid_by_govt, 2),
            "total_sum_insured": round(sum_insured, 2),
        },
        "terms_and_conditions": [
            "The policy is valid for one year from the date of issuance.",
            "Claims must be reported within 30 days of the incident.",
            "The insured must follow recommended agricultural practices.",
            "The insurer reserves the right to inspect the farm before claim settlement.",
        ],
    }
    return policy_data
