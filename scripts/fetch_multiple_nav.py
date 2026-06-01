import requests
import pandas as pd
from pathlib import Path

# Create raw folder
raw_folder = Path("data/raw")
raw_folder.mkdir(parents=True, exist_ok=True)

schemes = {
    "SBI_Bluechip": 119551,
    "ICICI_Bluechip": 120503,
    "Nippon_LargeCap": 118632,
    "Axis_Bluechip": 119092,
    "Kotak_Bluechip": 120841
}

for fund_name, scheme_code in schemes.items():

    url = f"https://api.mfapi.in/mf/{scheme_code}"

    print(f"Fetching {fund_name}...")

    response = requests.get(url)

    if response.status_code == 200:

        data = response.json()

        df = pd.DataFrame(data["data"])

        file_name = raw_folder / f"{fund_name}.csv"

        df.to_csv(file_name, index=False)

        print(f"Saved: {file_name}")

    else:
        print(f"Failed: {fund_name}")

print("\nAll downloads completed.")