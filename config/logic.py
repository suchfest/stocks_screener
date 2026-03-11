import yfinance as yf

import pandas as pd
from config.indicators import calculate_rsi

def csv_import(path):
    return pd.read_csv(path)

def valid_data(rows):
    if len(rows) < 14:
        return False
    return True

def rsi_filter(value):
    if value <= 30:
        return True
    return False

def fetch_price(ticker):
    stock = yf.Ticker(ticker)
    history = stock.history(period="3mo", interval="1d")
    df = history['Close']
    return df


def fetcher(df):
    results = [] 
    for ticker in df["ticker"]: 
        prices = fetch_price(ticker)
        if not valid_data(prices):
            continue
        rsi = calculate_rsi(prices) 
        last = rsi.iloc[-1]
        results.append({"ticker":ticker,"rsi": last}) 
    return results

def filtered(results):
    filtered = []
    for result in results:
        oversold = rsi_filter(result["rsi"]) 
        if oversold: 
            filtered.append(result) 
    return filtered