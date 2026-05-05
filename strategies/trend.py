from indicators.ema import calculate_ema_atr
from indicators.rsi import calculate_rsi, rsi_len


rsi_window = rsi_len
obv_sma_len = 20
structure_len = 20
trend_grace_period = 5


def pro_confluence_strategy(df):
    df = df.copy()

    # 1. trend
    df = calculate_ema_atr(df)
    is_bull_now = df["emaBull"] is True
    was_false_recently = (
        df["emaBull"].shift(1).rolling(window=trend_grace_period).min() == 0
    )
    fresh_bull = is_bull_now & was_false_recently

    # 2. rsi
    rsi = calculate_rsi(df["close"], length=rsi_window)
    rsi_not_overbought = rsi < 60

    # 3. volume
    obv = df.ta.obv()
    if obv is None:
        return False
    obv_sma = obv.ta.sma(length=obv_sma_len)
    if obv_sma is None:
        return False
    volume_confirmed = obv > obv_sma

    # 4. donchian
    dc = df.ta.donchian(lower_length=structure_len, upper_length=structure_len)
    if dc is None:
        return False
    mid_point = (dc.iloc[:, 2] + dc.iloc[:, 0]) / 2
    above_structure = df["close"] > mid_point

    return bool(
        fresh_bull.fillna(False).iloc[-1]
        and rsi_not_overbought.fillna(False).iloc[-1]
        and volume_confirmed.fillna(False).iloc[-1]
        and above_structure.fillna(False).iloc[-1]
    )
