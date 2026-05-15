"""
this file requires you to download the raw csvs from PSE website and save them in the raw_csvs folder
"""

import pandas as pd
import country_converter as coco
import os


output_file = "inputs/xetra_stocks.csv"



df1 = pd.read_csv('/raw_csvs/xetra - General Standard.csv', skiprows=7, usecols=[1,2,5])
df1.rename(columns={'Trading Symbol': 'ticker'}, inplace=True)
df1['ticker'] = df1['ticker'].str.strip()
df1['ticker'] = df1['ticker'].astype(str) + '.F'

df2 = pd.read_csv('/raw_csvs/xetra - Prime Standard.csv', skiprows=7, usecols=[1,2,5])
df2.rename(columns={'Trading Symbol': 'ticker'}, inplace=True)
df2['ticker'] = df2['ticker'].str.strip()
df2['ticker'] = df2['ticker'].astype(str) + '.F'

df = pd.concat([df1, df2])
df['Country'] = coco.convert(names=df['Country'], to='ISO2')

# Save to the new path
df.to_csv(output_file, index=False)

print("done")
