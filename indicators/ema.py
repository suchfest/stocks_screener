import pandas_ta as ta


ema_fast_len = 30
ema_slow_len = 60
ema_margin_atr_len = 60
ema_margin_atr_mult = 0.30


def calculate_ema_atr(
    df,
    emaFastLen=ema_fast_len,
    emaSlowLen=ema_slow_len,
    emaMarginATRLen=ema_margin_atr_len,
    emaMarginATRMult=ema_margin_atr_mult,
):
    df["emaFast"] = ta.ema(df["close"], length=emaFastLen)
    df["emaSlow"] = ta.ema(df["close"], length=emaSlowLen)
    df["emaDiff"] = df["emaFast"] - df["emaSlow"]
    df["atr"] = ta.atr(
        high=df["high"],
        low=df["low"],
        close=df["close"],
        length=emaMarginATRLen,
    )
    df["emaBull"] = df["emaDiff"] > emaMarginATRMult * df["atr"]
    df["emaBear"] = df["emaDiff"] < -emaMarginATRMult * df["atr"]
    df["emaNeutral"] = ~(df["emaBull"] | df["emaBear"])

    return df
