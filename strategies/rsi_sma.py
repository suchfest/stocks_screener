from indicators.ma import calculate_sma
from indicators.rsi import calculate_rsi


def strategy_rsi_sma(df):
    # get current close price
    current_close = float(df["Close"].iloc[-1])

    # get current RSI
    rsi_series = calculate_rsi(df["Close"])
    current_rsi = float(rsi_series.iloc[-1])
    # get current 200 sma
    sma200_series = calculate_sma(df["Close"])
    current_sma200 = float(sma200_series.iloc[-1])

    # check if stock is oversold and higher 200 sma
    is_oversold = current_rsi < 30
    is_uptrend = current_close > current_sma200
    is_buy_rsi_sma = is_oversold and is_uptrend

    return is_buy_rsi_sma
