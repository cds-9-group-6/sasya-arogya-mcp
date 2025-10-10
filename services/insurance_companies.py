import random
import pandas as pd


# Load data from CSV files
def get_registered_insurers(reset_rates: bool = False) -> pd.DataFrame:
    try:
        companies_df = pd.read_csv("resources/insurance_companies.csv")
        # --- Data Cleaning: Force columns to be numbers right after loading ---
        companies_df["Rate_Multiplier"] = pd.to_numeric(
            companies_df["Rate_Multiplier"], errors="coerce"
        )
        # Drop rows with NaN values in 'Rate_Multiplier' column
        companies_df.dropna(subset=["Rate_Multiplier"], inplace=True)

        if reset_rates:
            # --- Data Cleaning: Reset Rate_Multiplier to random values between 1.0 and 3.0 ---
            companies_df["Rate_Multiplier"] = [
                round(random.uniform(0.8, 1.2), 2) for _ in range(len(companies_df))
            ]
            # Save the updated DataFrame back to the CSV file
            # companies_df.to_csv("resources\insurance_companies.csv", index=False)
    # -------------------------------------------------------------------------

    except FileNotFoundError:
        print(
            "Error: Make sure 'insurance_companies.csv' are in the reources directory."
        )
        exit()
    except Exception as e:
        print(f"A critical error occurred while loading or cleaning the CSV files: {e}")
        exit()
    except pd.errors.EmptyDataError:
        print("Error: One of the CSV files is empty.")
        exit()
    return companies_df


def get_insurance_companies(state: str = None) -> list:
    """
    Get list of available insurance companies.

    Args:
        state: Optional state to filter companies

    Returns:
        List of dictionaries with company information
    """
    try:
        companies_df = get_registered_insurers(reset_rates=False)

        # Filter by state if provided
        # Insurance companies are not based on the states, they are registered in difference places

        # if state:
        #     companies_df = companies_df[
        #         companies_df["State"].str.lower() == state.lower()
        #     ]

        # Convert to list of dictionaries
        companies = []
        for _, row in companies_df.iterrows():
            companies.append(
                {
                    "name": row.get("Company_Name", "Unknown"),
                    "address": row.get("Address", "Address not available"),
                    "state": row.get("State", "Unknown"),
                    "rate_multiplier": row.get("Rate_Multiplier", 1.0),
                }
            )

        return companies

    except Exception as e:
        print(f"Error getting insurance companies: {e}")
        # Return default companies if error
        return [
            {
                "name": "General Insurance Corporation of India",
                "address": "New Delhi, India",
                "state": "Delhi",
                "rate_multiplier": 1.0,
            },
            {
                "name": "Agriculture Insurance Company of India",
                "address": "Mumbai, India",
                "state": "Maharashtra",
                "rate_multiplier": 1.0,
            },
        ]
