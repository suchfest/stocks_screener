import pandas_ta as ta  # noqa: F401 - registers DataFrame.ta accessor for downstream code.


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
    df["emaFast"] = df.ta.ema(length=emaFastLen)
    df["emaSlow"] = df.ta.ema(length=emaSlowLen)
    df["emaDiff"] = df["emaFast"] - df["emaSlow"]
    df["atr"] = df.ta.atr(length=emaMarginATRLen)
    df["emaBull"] = df["emaDiff"] > emaMarginATRMult * df["atr"]
    df["emaBear"] = df["emaDiff"] < -emaMarginATRMult * df["atr"]
    df["emaNeutral"] = ~(df["emaBull"] | df["emaBear"])

    return df
