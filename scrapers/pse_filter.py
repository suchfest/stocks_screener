"""
this file requires you to download the raw csvs from PSE website and save them in the raw_csvs folder

https://live.euronext.com/en/markets/paris/equities/list

rename the file french_raw.csv in order to run (or change the naming inside the code itself)
"""

from pathlib import Path
import os
import pandas as pd


root = Path(__file__).resolve().parent.parent  # discoverable at any place of the repo
input_file = root / "raw_csvs" / "euronext_raw.csv"
output_file = root / "inputs" / "euronext.csv"


df = pd.read_csv(input_file, skiprows=[1, 2, 3], sep=";", usecols=["Name", "Symbol"])
df.rename(columns={"Symbol": "ticker"}, inplace=True)

df = df[["ticker", "Name"]]  # change place between columns

df["ticker"] = df["ticker"].astype(str) + ".PA"

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
