import pandas as pd

from indicators.rsi import calculate_rsi, rsi_len
from indicators.ma import calculate_sma, sma_long_len
from indicators.bb import calculate_bollinger_bands, bb_len



sma_slow_len = 50
rsi_max = 31.0

def strategy_dip(close, low, volume):
    """Last-bar bundle for ``config.logic.fetcher`` (trend, RSI dip, BB tag, liquidity)."""
    min_len = max(sma_long_len, sma_slow_len, bb_len, 20) + 1
    if len(close) < min_len:
        return {"valid": False}

    rsi_s = calculate_rsi(close)
    sma50_s = close.rolling(window=sma_slow_len, min_periods=sma_slow_len).mean()
    sma200_s = calculate_sma(close)
    _, _, bb_lower_s = calculate_bollinger_bands(close)
    #adv20_s = volume.rolling(window=20, min_periods=20).mean()

    rsi = float(rsi_s.iloc[-1])
    sma50 = float(sma50_s.iloc[-1])
    sma200 = float(sma200_s.iloc[-1])
    bb_lower = float(bb_lower_s.iloc[-1])
    #adv20 = float(adv20_s.iloc[-1])
    c = float(close.iloc[-1]) #latest close price
    lo = float(low.iloc[-1]) #latest low price
    vol = float(volume.iloc[-1]) #latest volume

    if any(pd.isna(x) for x in (rsi, sma50, sma200, bb_lower, c, lo, vol)):
        return {"valid": False}
    if sma50 == 0:
        return {"valid": False}

    trend_pass = c > sma200
    dip_pass = rsi < rsi_max
    trigger_pass = lo < bb_lower
    #liquidity_pass = vol >= adv20
    #pullback_pct = (sma50 - c) / sma50 * 100.0
    buy = trend_pass and dip_pass and trigger_pass

    return {
        "valid": True,
        "close": c,
        "rsi": rsi,
        "sma50": sma50,
        "sma200": sma200,
        "trend_pass": trend_pass,
        "dip_pass": dip_pass,
        "trigger_pass": trigger_pass,
        #"liquidity_pass": liquidity_pass,
        #"pullback_pct": float(pullback_pct),
        #"adv20": adv20,
        "buy": buy,
    }


def triple_indicator_pass(
    close: float,
    low: float,      # Pass the daily low price here
    rsi: float,
    sma: float,      # Consider using a 100-day SMA instead of 200
    bb_lower: float,
) -> dict[str, bool]:
    
    # 1. Is it in an uptrend?
    sma_pass = close > sma
    
    rsi_pass = rsi < rsi_max
    
    # 3. Did it stretch down into the lower volatility band today?
    bb_pass = low < bb_lower 
    
    buy = sma_pass and rsi_pass and bb_pass
    return {
        "sma_pass": sma_pass,
        "rsi_pass": rsi_pass,
        "bb_pass": bb_pass,
        "buy": buy,
    }