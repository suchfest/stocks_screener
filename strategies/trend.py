import pandas_ta as ta

from indicators.ema import calculate_ema_atr
from indicators.rsi import calculate_rsi, rsi_len


def pro_confluence_strategy(
    df,
    rsi_window=rsi_len,
    obv_sma_len=20,
    structure_len=20,
    trend_grace_period=5,
):
    df = df.copy()
    # --- 1. TREND & MOMENTUM ---
    df = calculate_ema_atr(df)

    # "Fresh Trend" Logic: Bullish today, but was False at least once in the previous X candles
    is_bull_now = df["emaBull"] is True
    # If the minimum value in the last X shifted candles is 0 (False), it wasn't bullish the whole time
    was_false_recently = (
        df["emaBull"].shift(1).rolling(window=trend_grace_period).min() == 0
    )
    df["fresh_bull_trend"] = is_bull_now & was_false_recently

    # --- 2. OSCILLATOR (RSI) ---
    df["rsi"] = calculate_rsi(df["close"], length=rsi_window)
    # Check if we are NOT overbought (room to grow)
    df["rsi_not_overbought"] = df["rsi"] < 60

    # --- 3. VOLUME (On-Balance Volume) ---
    df["obv"] = ta.obv(df["close"], df["volume"])
    df["obv_sma"] = ta.sma(df["obv"], length=obv_sma_len)
    # Volume is "confirmed" if OBV is above its moving average
    df["volume_confirmed"] = df["obv"] > df["obv_sma"]

    # --- 4. STRUCTURE (Donchian Channels) ---
    # pandas_ta: col 0 = lower (DCL), 1 = mid (DCM), 2 = upper (DCU)
    dc = ta.donchian(
        df["high"],
        df["low"],
        lower_length=structure_len,
        upper_length=structure_len,
    )
    df["sup_level"] = dc.iloc[:, 0]
    df["res_level"] = dc.iloc[:, 2]

    # Structure Check: Is price breaking out or bouncing?
    df["mid_point"] = (df["res_level"] + df["sup_level"]) / 2
    df["above_structure"] = df["close"] > df["mid_point"]

    # --- THE FINAL BUY SIGNAL (CONFLUENCE) ---
    # 1. Trend recently flipped to Bullish (within last 5 candles)
    # 2. RSI says we aren't at the ceiling yet
    # 3. OBV says money is flowing in
    # 4. Price is in the upper half of its recent structure

    df["confluence_buy"] = (
        df["fresh_bull_trend"].fillna(False)
        & df["rsi_not_overbought"].fillna(False)
        & df["volume_confirmed"].fillna(False)
        & df["above_structure"].fillna(False)
    ).astype(bool)

    return df
