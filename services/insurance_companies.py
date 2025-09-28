import pandas as pd
import random
from datetime import datetime, timedelta


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


# return top 5 insurers based on Rate_Multiplier
def get_top_insurers(n=5):
    try:
        companies_df = pd.read_csv("resources/insurance_companies.csv")
        # Update Rate_Multiplier with random values between 0.8 and 1.2
        companies_df["Rate_Multiplier"] = [
            round(random.uniform(0.8, 1.2), 2) for _ in range(len(companies_df))
        ]
        # Sort by Rate_Multiplier ascending and get top n
        top_n = companies_df.sort_values("Rate_Multiplier").head(n)
        # Return list of tuples (Company Name, Rate_Multiplier)
        return list(zip(top_n["Company Name"], top_n["Rate_Multiplier"]))
    except Exception as e:
        print(f"Error in get_top_insurers: {e}")
        return []


def get_top_insurers_prompt(n=5):
    top_insurers = get_top_insurers(n)
    # Format as a prompt message
    prompt_text = "Top insurers and their rate multipliers:\n"
    for name, rate in top_insurers:
        prompt_text += f"- {name}: {rate}\n"
    return {"prompt": prompt_text}
