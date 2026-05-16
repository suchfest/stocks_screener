"""
this file requires you to download the raw csvs from PSE website and save them in the raw_csvs folder

https://live.euronext.com/en/markets/paris/equities/list

rename the file french_raw.csv in order to run (or change the naming inside the code itself)
"""

from pathlib import Path

import pandas as pd


root = Path(__file__).resolve().parent.parent  # discoverable at any place of the repo
input_file = root / "raw_csvs" / "euronext_raw.csv"
output_file = root / "inputs" / "euronext.csv"


df = pd.read_csv(input_file, skiprows=[1, 2, 3], sep=";", usecols=["Name", "Symbol"])
df.rename(columns={"Symbol": "ticker"}, inplace=True)

df = df[["ticker", "Name"]]  # change place between columns

df["ticker"] = df["ticker"].astype(str) + ".PA"


# Save to the new path
df.to_csv(output_file, index=False)
