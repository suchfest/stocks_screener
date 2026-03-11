import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D



def rma(series: pd.Series, length: int) -> pd.Series:
    """Wilder's Smoothed Moving Average (RMA), equivalent to Pine's ta.rma."""
    alpha = 1.0 / length
    return series.ewm(alpha=alpha, adjust=False).mean()


def calculate_rsi(source: pd.Series, length: int = 14) -> pd.Series:
    """Calculate RSI using Wilder's smoothing method."""
    change = source.diff()
    up   = rma(change.clip(lower=0), length)
    down = rma((-change).clip(lower=0), length)

    rsi = np.where(
        down == 0, 100,
        np.where(up == 0, 0, 100 - (100 / (1 + up / down)))
    )
    return pd.Series(rsi, index=source.index, name="RSI")



def calculate_ma(source: pd.Series, length: int, ma_type: str) -> pd.Series:
    """
    Smoothing MA types:
      'SMA', 'SMA + Bollinger Bands', 'EMA', 'SMMA (RMA)', 'WMA', 'VWMA'
    For VWMA pass volume separately (not supported here without volume).
    """
    match ma_type:
        case "SMA" | "SMA + Bollinger Bands":
            return source.rolling(length).mean()
        case "EMA":
            return source.ewm(span=length, adjust=False).mean()
        case "SMMA (RMA)":
            return rma(source, length)
        case "WMA":
            weights = np.arange(1, length + 1)
            return source.rolling(length).apply(
                lambda x: np.dot(x, weights) / weights.sum(), raw=True
            )
        case _:
            return pd.Series(np.nan, index=source.index)


def calculate_bollinger_bands(source: pd.Series, length: int, mult: float = 2.0):
    """Returns (sma, upper_band, lower_band)."""
    sma   = source.rolling(length).mean()
    stdev = source.rolling(length).std(ddof=0)
    return sma, sma + mult * stdev, sma - mult * stdev



def pivot_low(series: pd.Series, left: int, right: int) -> pd.Series:
    """Returns True where series has a pivot low."""
    result = pd.Series(False, index=series.index)
    for i in range(left, len(series) - right):
        window = series.iloc[i - left: i + right + 1]
        if series.iloc[i] == window.min():
            result.iloc[i] = True
    return result


def pivot_high(series: pd.Series, left: int, right: int) -> pd.Series:
    """Returns True where series has a pivot high."""
    result = pd.Series(False, index=series.index)
    for i in range(left, len(series) - right):
        window = series.iloc[i - left: i + right + 1]
        if series.iloc[i] == window.max():
            result.iloc[i] = True
    return result


def detect_divergences(
    rsi: pd.Series,
    price_low: pd.Series,
    price_high: pd.Series,
    lookback_left: int  = 5,
    lookback_right: int = 5,
    range_lower: int    = 5,
    range_upper: int    = 60,
):
    """
    Detect regular bullish and bearish RSI divergences.

    Returns two boolean Series:
      bull_cond — Regular Bullish Divergence (price LL, RSI HL)
      bear_cond — Regular Bearish Divergence (price HH, RSI LH)
    """
    pl = pivot_low(rsi,  lookback_left, lookback_right)
    ph = pivot_high(rsi, lookback_left, lookback_right)

    n = len(rsi)
    bull_cond = pd.Series(False, index=rsi.index)
    bear_cond = pd.Series(False, index=rsi.index)

    # ── Bullish divergence ──
    pl_indices = rsi.index[pl].tolist()
    for j, idx in enumerate(pl_indices):
        if j == 0:
            continue
        prev_idx = pl_indices[j - 1]
        bars_between = rsi.index.get_loc(idx) - rsi.index.get_loc(prev_idx) # type: ignore
        if not (range_lower <= bars_between <= range_upper):
            continue
        rsi_hl    = rsi[idx]   > rsi[prev_idx]
        price_ll  = price_low[idx] < price_low[prev_idx]
        if rsi_hl and price_ll:
            bull_cond[idx] = True

    # ── Bearish divergence ──
    ph_indices = rsi.index[ph].tolist()
    for j, idx in enumerate(ph_indices):
        if j == 0:
            continue
        prev_idx = ph_indices[j - 1]
        bars_between = rsi.index.get_loc(idx) - rsi.index.get_loc(prev_idx)
        if not (range_lower <= bars_between <= range_upper):
            continue
        rsi_lh    = rsi[idx]    < rsi[prev_idx]
        price_hh  = price_high[idx] > price_high[prev_idx]
        if rsi_lh and price_hh:
            bear_cond[idx] = True

    return bull_cond, bear_cond




def plot_rsi(
    df: pd.DataFrame,
    rsi_length:      int   = 14,
    source_col:      str   = "close",
    ma_type:         str   = "SMA",          # "None" to disable
    ma_length:       int   = 14,
    bb_mult:         float = 2.0,
    show_divergence: bool  = True,
):
    """
    Plot RSI with optional smoothing MA / Bollinger Bands and divergence labels.

    df must contain at least a column matching `source_col`.
    For divergence detection, df must also contain 'low' and 'high' columns.
    """
    source = df[source_col]
    rsi = calculate_rsi(source, rsi_length)

    fig, ax = plt.subplots(figsize=(14, 5))
    fig.patch.set_facecolor("#131722")
    ax.set_facecolor("#131722")

    # RSI line
    ax.plot(rsi.index, rsi.values, color="#7E57C2", linewidth=1.5, label="RSI", zorder=3)

    # Overbought / oversold gradient fills
    ax.fill_between(rsi.index, 70, rsi.values.clip(min=70),
                    color="green", alpha=0.25, label="_ob fill")
    ax.fill_between(rsi.index, rsi.values.clip(max=30), 30,
                    color="red",   alpha=0.25, label="_os fill")

    # Background band fill (30–70)
    ax.fill_between(rsi.index, 30, 70, color="#7E57C2", alpha=0.08)

    # H-lines
    for level, label, alpha in [(70, "Upper (70)", 1.0),
                                  (50, "Mid  (50)", 0.4),
                                  (30, "Lower (30)", 1.0)]:
        ax.axhline(level, color="#787B86", linewidth=0.8, alpha=alpha, linestyle="--")

    # ── Smoothing MA / Bollinger Bands ──
    if ma_type != "None":
        if ma_type == "SMA + Bollinger Bands":
            sma, bb_upper, bb_lower = calculate_bollinger_bands(rsi, ma_length, bb_mult)
            ax.plot(rsi.index, sma.values,      color="yellow", linewidth=1.2, label="RSI SMA")
            ax.plot(rsi.index, bb_upper.values, color="green",  linewidth=0.9, label="BB Upper")
            ax.plot(rsi.index, bb_lower.values, color="green",  linewidth=0.9, label="BB Lower")
            ax.fill_between(rsi.index, bb_upper.values, bb_lower.values,
                            color="green", alpha=0.07, label="_bb fill")
        else:
            smoothing = calculate_ma(rsi, ma_length, ma_type)
            ax.plot(rsi.index, smoothing.values, color="yellow", linewidth=1.2,
                    label=f"RSI {ma_type}")

    # ── Divergence ──
    if show_divergence and "low" in df.columns and "high" in df.columns:
        bull, bear = detect_divergences(rsi, df["low"], df["high"])

        for idx in rsi.index[bull]:
            ax.annotate("▲ Bull", xy=(idx, rsi[idx]),
                        xytext=(0, -20), textcoords="offset points",
                        ha="center", fontsize=7, color="white",
                        bbox=dict(boxstyle="round,pad=0.3", fc="green", alpha=0.85))

        for idx in rsi.index[bear]:
            ax.annotate("▼ Bear", xy=(idx, rsi[idx]),
                        xytext=(0, 12), textcoords="offset points",
                        ha="center", fontsize=7, color="white",
                        bbox=dict(boxstyle="round,pad=0.3", fc="red", alpha=0.85))

    # Styling
    ax.set_ylim(0, 100)
    ax.set_xlim(rsi.index[0], rsi.index[-1])
    ax.set_title("Relative Strength Index (RSI)", color="white", fontsize=13, pad=10)
    ax.set_ylabel("RSI", color="#9B9EA3")
    ax.tick_params(colors="#9B9EA3", labelsize=8)
    for spine in ax.spines.values():
        spine.set_edgecolor("#2A2E39")

    ax.legend(
        handles=[
            Line2D([0], [0], color="#7E57C2", linewidth=1.5, label="RSI"),
            mpatches.Patch(color="green", alpha=0.4, label="Overbought fill"),
            mpatches.Patch(color="red",   alpha=0.4, label="Oversold fill"),
        ],
        facecolor="#1E222D", edgecolor="#2A2E39", labelcolor="white", fontsize=8,
        loc="upper left",
    )

    plt.tight_layout()
    return fig, ax, rsi