import pandas as pd


def get_crop_premium_data():
    try:
        crop_df = pd.read_csv("resources/crop_data.csv")
        crop_df["Scale of Finance (Rs/Hectare)"] = pd.to_numeric(
            crop_df["Scale of Finance (Rs/Hectare)"], errors="coerce"
        )
        crop_df["Actuarial Premium Rate (%)"] = pd.to_numeric(
            crop_df["Actuarial Premium Rate (%)"], errors="coerce"
        )
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
    return crop_df
