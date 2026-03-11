def rma(series, length):
    return series.ewm(alpha=1/length, adjust=False).mean()

def calculate_rsi(source, length=14):
    change = source.diff()
    up   = rma(change.clip(lower=0), length)
    down = rma((-change).clip(lower=0), length)
    return 100 - (100 / (1 + up / down))