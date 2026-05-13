import yfinance as yf

from strategies.dip import strategy_dip
from strategies.rsi_sma import strategy_rsi_sma
from strategies.trend import strategy_trend


def valid_data(rows):
    return len(rows) >= 200


# 1. Create a unified fetch_data function
def fetch_data(ticker, timeframe="1d"):
    stock = yf.Ticker(ticker)

    if timeframe == "1h":
        return stock.history(period="3m", interval="1h")
    elif timeframe == "4h":
        return stock.history(period="1y", interval="4h")
    elif timeframe == "1d":
        return stock.history(period="1y", interval="1d")
    else:
        raise ValueError("Invalid timeframe. Choose '1h', '4h', or '1d'.")


# 2. Update fetchers to accept the timeframe parameter
def fetcher_dip(ticker, timeframe="1d"):
    prices = fetch_data(ticker, timeframe)
    if not valid_data(prices):
        return None

    buy_dip = strategy_dip(prices)
    if not buy_dip:
        return None

    return {"ticker": ticker, "timeframe": timeframe}


def fetcher_trend(ticker, timeframe="1d"):
    prices = fetch_data(ticker, timeframe)
    if not valid_data(prices):
        return None

    buy_trend = strategy_trend(prices)
    if not buy_trend:
        return None

    return {"ticker": ticker, "timeframe": timeframe}


def fetcher_rsi_sma(ticker, timeframe="1d"):
    prices = fetch_data(ticker, timeframe)
    if not valid_data(prices):
        return None

    buy_rsi_sma = strategy_rsi_sma(prices)
    if not buy_rsi_sma:
        return None

    return {"ticker": ticker, "timeframe": timeframe}
