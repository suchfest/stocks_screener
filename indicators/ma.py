sma_long_len = 200
ema_long_len = 200


def calculate_sma(series, length=sma_long_len):
    return series.rolling(window=length, min_periods=50).mean()


def calculate_ema(series, length=ema_long_len):
    return series.ewm(span=length, adjust=False).mean()
