from concurrent.futures import ThreadPoolExecutor

import pandas as pd
import yfinance as yf
from tqdm import tqdm

from strategies.dip import strategy_dip


# CSV handling


def csv_import(path):
    return pd.read_csv(path)


def csv_output(results, path):
    if not results:
        return
    df = pd.DataFrame(results)
    if "ticker" not in df.columns:
        raise ValueError
    return df.to_csv(path, index=False)


# data handling


def valid_data(rows):
    return len(rows) >= 50


def rsi_filter(value):
    return value <= 30


def filtered(results):
    filtered = []
    for result in results:
        oversold = rsi_filter(result["rsi"])
        if oversold:
            filtered.append(result)
    return filtered


# ticker fetcher for dip_strategy


def fetch_dip(ticker):
    stock = yf.Ticker(ticker)
    history = stock.history(period="3mo", interval="1d")  # for daily
    return history


def fetcher_dip(ticker):
    prices = fetch_dip(ticker)
    if not valid_data(prices):
        return None

    buy = strategy_dip(prices["Close"], prices["Low"])
    if not buy:
        return None

    return {"ticker": ticker}


# multiple workers to iterate


def worker(df):
    tickers = df["ticker"].tolist()
    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(tqdm(executor.map(fetcher_dip, tickers), total=len(tickers)))
    return [r for r in results if r is not None]
