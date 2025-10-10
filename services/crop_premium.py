import pandas as pd
from services.shared_utils import get_crop_premium_data
from services.insurance_advisor import recommend_insurance, get_farmer_share_percent
from services.insurance_certificate import generate_certificate
from services.insurance_companies import (
    get_insurance_companies,
    get_registered_insurers,
)



# Load data from CSV files
def get_crop_premium_data():
    try:
        crop_df = pd.read_csv("resources/crop_data.csv")

        # --- Data Cleaning: Force columns to be numbers right after loading ---
        crop_df["Scale of Finance (Rs/Hectare)"] = pd.to_numeric(
            crop_df["Scale of Finance (Rs/Hectare)"], errors="coerce"
        )
        crop_df["Actuarial Premium Rate (%)"] = pd.to_numeric(
            crop_df["Actuarial Premium Rate (%)"], errors="coerce"
        )

        # Remove any rows that had bad data to ensure calculations never fail.
        crop_df.dropna(
            subset=["Scale of Finance (Rs/Hectare)", "Actuarial Premium Rate (%)"],
            inplace=True,
        )
    except FileNotFoundError:
        print("Error: Make sure 'crop_data.csv' is in the resources directory.")
        exit()
    except Exception as e:
        print(f"A critical error occurred while loading or cleaning the CSV files: {e}")
        exit()
    except pd.errors.EmptyDataError:
        print("Error: One of the CSV files is empty.")
        exit()
    return crop_df


def calculate_premium(crop: str, area_hectare: float, state: str) -> dict:
    """
    Calculate insurance premium for a specific crop and area.

    Args:
        crop: Name of the crop
        area_hectare: Area in hectares
        state: State where the crop is grown

    Returns:
        Dictionary with premium calculation details
    """
    try:
        crop_df = get_crop_premium_data()

        # Find the crop data (case-insensitive search)
        crop_data = crop_df[crop_df["Crop"].str.lower() == crop.lower()]

        if crop_data.empty:
            # Return default values if crop not found
            return {
                "premium_per_hectare": 0.0,
                "total_premium": 0.0,
                "govt_subsidy": 0.0,
                "farmer_contribution": 0.0,
                "sum_insured_per_hectare": 0.0,
                "actuarial_rate": 0.0,
            }

        # Get the first matching crop data
        crop_info = crop_data.iloc[0]
        sum_insured_per_hectare = crop_info["Scale of Finance (Rs/Hectare)"]
        actuarial_rate = crop_info["Actuarial Premium Rate (%)"]

        # Calculate premium
        # Get the premium from the insurers
        # Load insurance companies data and reset rates (randomize) for demo purposes
        companies_df = get_registered_insurers(reset_rates=False)

        crop_info = crop_df[crop_df["Crop"].str.lower() == crop.lower()]
        if crop_info.empty:
            raise ValueError(f"Crop '{crop}' not found.")
        crop_info = crop_info.iloc[0]

        scale_of_finance = crop_info["Scale of Finance (Rs/Hectare)"]
        actuarial_rate = crop_info["Actuarial Premium Rate (%)"] / 100

        farmer_share_percent = get_farmer_share_percent(crop_info["Season"])
        sum_insured = scale_of_finance * area_hectare

        # Find the insurance company offering the lowest gross premium
        best_company = None
        lowest_gross_premium = float("inf")
        for index, company in companies_df.iterrows():
            rate_multiplier = company["Rate_Multiplier"]
            company_gross_premium = sum_insured * actuarial_rate * rate_multiplier
            if company_gross_premium < lowest_gross_premium:
                lowest_gross_premium = company_gross_premium
                best_company = company
        insurance_company_name = best_company["Company_Name"] if best_company is not None else "No company available"
        company_address = best_company["Address"] if best_company is not None else "Address not available"

        # if best_company is None:
        #     raise ValueError("No insurance companies available.")

        sum_insured_per_hectare = sum_insured
        premium_paid_by_farmer = company_gross_premium * farmer_share_percent
        premium_paid_by_govt = lowest_gross_premium - premium_paid_by_farmer
        premium_per_hectare = lowest_gross_premium / area_hectare

        return {
            "premium_per_hectare": premium_per_hectare,
            "total_premium": lowest_gross_premium,
            "govt_subsidy": premium_paid_by_govt,
            "farmer_contribution": premium_paid_by_farmer,
            "sum_insured_per_hectare": sum_insured_per_hectare,
            "actuarial_rate": actuarial_rate,
            'insurance_company_name': insurance_company_name,
            'company_address': company_address
        }

    except Exception as e:
        print(f"Error calculating premium: {e}")
        return {
            'premium_per_hectare': 0.0,
            'total_premium': 0.0,
            'govt_subsidy': 0.0,
            'farmer_contribution': 0.0,
            'sum_insured_per_hectare': 0.0,
            'actuarial_rate': 0.0,
            'insurance_company_name': "No company available",
            'company_address': "Address not available"
        }
