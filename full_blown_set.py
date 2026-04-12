import numpy as np
import pandas as pd

# --- CORE INDICATOR MATH ---

def rma(series: pd.Series, length: int) -> pd.Series:
    """Wilder's Smoothed Moving Average (RMA)."""
    alpha = 1.0 / length
    return series.ewm(alpha=alpha, adjust=False).mean()

def calculate_rsi(source: pd.Series, length: int = 14) -> pd.Series:
    """Standard RSI calculation."""
    change = source.diff()
    up = rma(change.clip(lower=0), length)
    down = rma((-change).clip(lower=0), length)
    rsi = np.where(down == 0, 100, np.where(up == 0, 0, 100 - (100 / (1 + up / down))))
    return pd.Series(rsi, index=source.index, name="RSI")

def calculate_macd(source: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
    """MACD Line and Signal Line calculation."""
    fast_ema = source.ewm(span=fast, adjust=False).mean()
    slow_ema = source.ewm(span=slow, adjust=False).mean()
    macd_line = fast_ema - slow_ema
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    return macd_line, signal_line

# --- SIGNAL GENERATION LOGIC ---

def generate_signals(df: pd.DataFrame):
    """
    High-Confluence Decision Script:
    1. Trend: Price > SMA 200 (Long-term health check)
    2. Value: RSI was recently < 30 (Oversold setup)
    3. Momentum: Price > EMA 8 AND MACD Bullish Cross (Entry triggers)
    4. Confirmation: Volume > Avg (Institutional backing)
    """
    # Create copy to avoid modifying original dataframe
    data = df.copy()

    # 1. Calculate Technical Components
    rsi = calculate_rsi(data['close'])
    sma200 = data['close'].rolling(window=200).mean()
    ema8 = data['close'].ewm(span=8, adjust=False).mean()
    macd_line, signal_line = calculate_macd(data['close'])
    avg_vol = data['volume'].rolling(window=20).mean()

    # 2. Define Logical Components
    # RSI Setup: Was it oversold in the last 5 bars? 
    # (Gives room for MACD to cross after the price bottom)
    was_oversold = rsi.rolling(window=5).min() < 30
    
    # Trend Filter
    is_trending_up = data['close'] > sma200
    
    # Momentum Trigger: MACD Crossover + Price above short-term EMA
    macd_bull_cross = (macd_line > signal_line) & (macd_line.shift(1) <= signal_line.shift(1))
    above_ema8 = data['close'] > ema8
    
    # Volume Confirmation
    high_volume = data['volume'] > avg_vol

    # 3. Final Decision (The "Buy" Signal)
    buy_signal = was_oversold & is_trending_up & macd_bull_cross & above_ema8 & high_volume

    return buy_signal

# Example Usage:
# df['buy_signal'] = generate_signals(df)
# trades = df[df['buy_signal'] == True]