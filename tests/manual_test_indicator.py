"""
run this and check the RSI value. Compare it to the tool you personally use
(for the it's TradingView)
"""

import yfinance as yf
from config.indicators import calculate_rsi


ticker = yf.Ticker("MSFT")
df = ticker.history(period="3mo", interval="1d")
rsi_series = calculate_rsi(df['Close'])

print(f"{rsi_series.iloc[-1]:.1f}")

"""
if a list of prices is needed for test_indicator.py

print(df['Close'].tolist())
"""

