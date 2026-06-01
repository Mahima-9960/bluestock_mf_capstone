import requests
import pandas as pd
from pathlib import Path

# Create raw data folder if it doesn't exist
raw_folder = Path("data/raw")
raw_folder.mkdir(parents=True, exist_ok=True)

# HDFC Top 100 Direct Fund
scheme_code = 125497
url = f"https://api.mfapi.in/mf/{scheme_code}"

print("Fetching NAV data...")

response = requests.get(url)

if response.status_code == 200:
    data = response.json()

    nav_df = pd.DataFrame(data["data"])

    file_path = raw_folder / "HDFC_Top100_NAV.csv"

    nav_df.to_csv(file_path, index=False)

    print("File saved successfully!")
    print(f"Location: {file_path}")
    print("\nFirst 5 rows:")
    print(nav_df.head())

else:
    print("Failed to fetch data")