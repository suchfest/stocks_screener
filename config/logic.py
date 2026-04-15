from concurrent.futures import ThreadPoolExecutor

import pandas as pd
import yfinance as yf
from tqdm import tqdm

from config.indicators import calculate_rsi


# CSV handling


def csv_import(path):
    return pd.read_csv(path)


def csv_output(results, path):
    df = pd.DataFrame(results)
    if "ticker" not in df.columns or "rsi" not in df.columns:
        raise ValueError
    else:
        return df.to_csv(path, index=False)


# data handling


def valid_data(rows):
    if len(rows) < 14:
        return False
    return True


def rsi_filter(value):
    if value <= 30:
        return True
    return False


def filtered(results):
    filtered = []
    for result in results:
        oversold = rsi_filter(result["rsi"])
        if oversold:
            filtered.append(result)
    return filtered


# ticker fetcher


def fetch_price(ticker):
    stock = yf.Ticker(ticker)
    history = stock.history(period="3mo", interval="1d")  # for daily RSI
    df = history["Close"]
    return df


# get ticker price


def fetcher(ticker):
    prices = fetch_price(ticker)
    if not valid_data(prices):
        return None
    rsi = calculate_rsi(prices)
    last = rsi.iloc[-1]
    return {"ticker": ticker, "rsi": float(last)}


# multiple workers to iterate


def worker(df):
    tickers = df["ticker"].tolist()
    with ThreadPoolExecutor(max_workers=5) as executor:
        results = list(tqdm(executor.map(fetcher, tickers), total=len(tickers)))
    return [r for r in results if r is not None]
