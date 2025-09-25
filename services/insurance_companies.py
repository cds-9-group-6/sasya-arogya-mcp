import pandas as pd
import random
from datetime import datetime, timedelta


# Load data from CSV files
def get_registered_insurers():
    try:
        companies_df = pd.read_csv("resources\insurance_companies.csv")
        # --- Data Cleaning: Force columns to be numbers right after loading ---
        companies_df["Rate_Multiplier"] = pd.to_numeric(
            companies_df["Rate_Multiplier"], errors="coerce"
        )

        companies_df.dropna(subset=["Rate_Multiplier"], inplace=True)
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
