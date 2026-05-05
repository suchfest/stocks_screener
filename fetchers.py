import yfinance as yf

from strategies.dip import strategy_dip
from strategies.rsi_sma import strategy_rsi_sma
from strategies.trend import strategy_trend


def valid_data(rows):
    return len(rows) >= 200


def fetch_data(ticker):
    stock = yf.Ticker(ticker)
    history = stock.history(period="1y", interval="1d")  # for daily
    return history


def fetcher_dip(ticker):
    prices = fetch_data(ticker)
    if not valid_data(prices):
        return None

    buy_dip = strategy_dip(prices)
    if not buy_dip:
        return None

    return {"ticker": ticker}


def fetcher_trend(ticker):
    prices = fetch_data(ticker)
    if not valid_data(prices):
        return None

    buy_trend = strategy_trend(prices)
    if not buy_trend:
        return None

    return {"ticker": ticker}


def fetcher_rsi_sma(ticker):
    prices = fetch_data(ticker)
    if not valid_data(prices):
        return None
    buy_rsi_sma = strategy_rsi_sma(prices)
    if not buy_rsi_sma:
        return None

    return {"ticker": ticker}
