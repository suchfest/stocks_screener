rsi_len = 10


def calculate_rsi(source, length=rsi_len):
    delta = source.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    # calculate the initial SMA
    initial_gain = gain.rolling(window=length).mean()
    initial_loss = loss.rolling(window=length).mean()

    # calculate Wilder's Smoothing (RMA)
    gain_rma = gain.ewm(alpha=1/length, adjust=False).mean()
    loss_rma = loss.ewm(alpha=1/length, adjust=False).mean()

    # replace the early values with the initial SMA
    gain_rma.iloc[:length] = initial_gain.iloc[:length]
    loss_rma.iloc[:length] = initial_loss.iloc[:length]

    # calculate RSI
    rs = gain_rma / loss_rma
    return 100 - (100 / (1 + rs))
