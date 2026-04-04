from config.logic import valid_data, rsi_filter, fetch_price, csv_import, fetcher, filtered, csv_output, worker
import yfinance as yf
import pandas as pd

df = csv_import("inputs/DE_stocks.csv")
fetch = worker(df)
filter = filtered(fetch)
output = csv_output(filter, "outputs/rsi.csv")

print("done")