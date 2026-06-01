import pandas as pd
from pathlib import Path

# Folder containing CSV files
data_folder = Path("data/raw")

# Get all CSV files
csv_files = list(data_folder.glob("*.csv"))

print(f"\nFound {len(csv_files)} CSV files\n")

for file in csv_files:

    print("=" * 70)
    print(f"FILE NAME : {file.name}")

    df = pd.read_csv(file)

    print("\nSHAPE:")
    print(df.shape)

    print("\nDATA TYPES:")
    print(df.dtypes)

    print("\nFIRST 5 ROWS:")
    print(df.head())

    print("\n")