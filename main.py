from config.logic import valid_data, rsi_filter, fetch_price, csv_import, fetcher, filtered
import yfinance as yf
import pandas as pd

df = csv_import("inputs/test.csv")
fetch = fetcher(df)
output = filtered(fetch)

print(output)