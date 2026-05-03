bb_len = 20
bb_num_std = 1.5


def calculate_bollinger_bands(close_series, length=bb_len, num_std=bb_num_std):
    """Middle, upper, and lower Bollinger Bands."""
    sma = close_series.rolling(window=length).mean()
    std = close_series.rolling(window=length).std()

    upper_band = sma + (std * num_std)
    lower_band = sma - (std * num_std)

    return sma, upper_band, lower_band
