import pandas as pd


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
        crop_data = crop_df[crop_df['Crop'].str.lower() == crop.lower()]
        
        if crop_data.empty:
            # Return default values if crop not found
            return {
                'premium_per_hectare': 0.0,
                'total_premium': 0.0,
                'govt_subsidy': 0.0,
                'farmer_contribution': 0.0,
                'sum_insured_per_hectare': 0.0,
                'actuarial_rate': 0.0
            }
        
        # Get the first matching crop data
        crop_info = crop_data.iloc[0]
        sum_insured_per_hectare = crop_info['Scale of Finance (Rs/Hectare)']
        actuarial_rate = crop_info['Actuarial Premium Rate (%)']
        
        # Calculate premium
        premium_per_hectare = (sum_insured_per_hectare * actuarial_rate) / 100
        total_premium = premium_per_hectare * area_hectare
        
        # Government subsidy (typically 90% for most crops)
        govt_subsidy = total_premium * 0.9
        farmer_contribution = total_premium * 0.1
        
        return {
            'premium_per_hectare': premium_per_hectare,
            'total_premium': total_premium,
            'govt_subsidy': govt_subsidy,
            'farmer_contribution': farmer_contribution,
            'sum_insured_per_hectare': sum_insured_per_hectare,
            'actuarial_rate': actuarial_rate
        }
        
    except Exception as e:
        print(f"Error calculating premium: {e}")
        return {
            'premium_per_hectare': 0.0,
            'total_premium': 0.0,
            'govt_subsidy': 0.0,
            'farmer_contribution': 0.0,
            'sum_insured_per_hectare': 0.0,
            'actuarial_rate': 0.0
        }
