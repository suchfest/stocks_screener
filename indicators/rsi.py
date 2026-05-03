rsi_len = 10


def calculate_rsi(source, length=rsi_len):
    delta = source.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    # 1. Calculate the initial SMA (TradingView "Warm-up")
    initial_gain = gain.rolling(window=length).mean()
    initial_loss = loss.rolling(window=length).mean()

    # 2. Calculate Wilder's Smoothing (RMA)
    gain_rma = gain.ewm(alpha=1 / length, adjust=False).mean()
    loss_rma = loss.ewm(alpha=1 / length, adjust=False).mean()

    # 3. Replace the early values with the initial SMA
    # This aligns the start of your data with TradingView's logic
    gain_rma.iloc[:length] = initial_gain.iloc[:length]
    loss_rma.iloc[:length] = initial_loss.iloc[:length]

    # 4. Calculate RSI
    rs = gain_rma / loss_rma
    return 100 - (100 / (1 + rs))
