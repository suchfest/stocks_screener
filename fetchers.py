import random
import time

import yfinance as yf
from curl_cffi import requests  # yahoo requirment

from strategies.dip import strategy_dip
from strategies.rsi_sma import strategy_rsi_sma
from strategies.trend import strategy_trend


# exactly what yahoo expects
shared_session = requests.Session(impersonate="chrome")  # type: ignore # FIX ME


def valid_data(rows):
    return len(rows) >= 200


def fetch_data(tickers, timeframe="1d"):
    # needed to seem like a human
    time.sleep(random.uniform(0.4, 1.2))

    kwargs = {
        "tickers": tickers,
        "auto_adjust": True,
        "group_by": "ticker",
        "progress": False,
        "session": shared_session,  # Uses your Chrome session!
    }

    if timeframe == "1h":
        return yf.download(period="3mo", interval="1h", **kwargs)
    elif timeframe == "4h":
        return yf.download(period="1y", interval="4h", **kwargs)
    elif timeframe == "1d":
        return yf.download(period="1y", interval="1d", **kwargs)
    else:
        raise ValueError("Invalid timeframe. Choose '1h', '4h', or '1d'.")


def fetcher_dip(tickers, timeframe="1d"):
    data = fetch_data(tickers, timeframe)
    if data is None or data.empty:
        return []
    results = []
    for ticker in tickers:
        prices = data[ticker].dropna()

        if not valid_data(prices):
            continue
        if not strategy_dip(prices):
            continue
        results.append({"ticker": ticker})

    return results


def fetcher_trend(tickers, timeframe="1d"):
    data = fetch_data(tickers, timeframe)
    if data is None or data.empty:
        return []
    results = []
    for ticker in tickers:
        prices = data[ticker].dropna()

        if not valid_data(prices):
            continue
        if not strategy_trend(prices):
            continue
        results.append({"ticker": ticker})

    return results


def fetcher_rsi_sma(tickers, timeframe="1d"):
    data = fetch_data(tickers, timeframe)
    if data is None or data.empty:
        return []
    results = []
    for ticker in tickers:
        prices = data[ticker].dropna()

        if not valid_data(prices):
            continue
        if not strategy_rsi_sma(prices):
            continue
        results.append({"ticker": ticker})

    return results
