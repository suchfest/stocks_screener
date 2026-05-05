import pandas as pd

from indicators.bb import bb_len, calculate_bollinger_bands
from indicators.ma import calculate_sma, sma_long_len
from indicators.rsi import calculate_rsi


sma_slow_len = 50
rsi_max = 31.0


def strategy_dip(close, low):
    min_len = max(sma_long_len, sma_slow_len, bb_len, 20) + 1
    if len(close) < min_len:
        return None

    rsi = float(calculate_rsi(close).iloc[-1])
    sma50 = float(
        close.rolling(window=sma_slow_len, min_periods=sma_slow_len).mean().iloc[-1]
    )
    sma200 = float(calculate_sma(close).iloc[-1])
    _, _, bb_lower_s = calculate_bollinger_bands(close)
    bb_lower = float(bb_lower_s.iloc[-1])
    c = float(close.iloc[-1])
    lo = float(low.iloc[-1])

    if any(pd.isna(x) for x in (rsi, sma50, sma200, bb_lower, c, lo)):
        return None
    if sma50 == 0:
        return None

    return (c > sma200) and (rsi < rsi_max) and (lo < bb_lower)
