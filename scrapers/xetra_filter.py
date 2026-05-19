"""
- this file requires you to download the raw csvs from XETRA website and save them in the raw_csvs folder

https://www.cashmarket.deutsche-boerse.com/cash-en/trading/Tradable-Instruments-Xetra/Downloads

- you need "T7 (Xetra) All tradable instruments"
- mv to /raw_csvs
- rename the file to xetra_raw.csv (or change the naming inside the code itself)
"""

from pathlib import Path
import os
import pandas as pd


root = Path(__file__).resolve().parent.parent  # discoverable at any place of the repo
input_file = root / "raw_csvs" / "xetra_raw.csv"
output_file = root / "inputs" / "xetra.csv"


df = pd.read_csv(input_file, skiprows=2, sep=";", usecols=["Mnemonic", "Instrument"])
df.rename(columns={"Mnemonic": "ticker"}, inplace=True)

df = df[["ticker", "Instrument"]]  # change place between columns

df["ticker"] = df["ticker"].astype(str) + ".DE"


# Save to the new path
project_root = os.path.dirname(os.path.abspath(__file__))
script_route = os.path.dirname(project_root)
output_path = os.path.join(script_route, output_file)
parent = os.path.dirname(output_path)
if parent:
    os.makedirs(parent, exist_ok=True)
df.to_csv(output_path, index=False)
# Save to the new path
df.to_csv(output_file, index=False)
        
print("done")
