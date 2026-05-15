# stocks-screener

A Python tool that reads a list of tickers from a CSVs, downloads price history via `yfinance`, and screens each symbol with one of three strategies. Matches are written to CSV under `outputs/`.

---

## What you need

- **Python 3.11+**
- Dependencies: `pandas`, `pandas-ta` (Trend / indicators), `yfinance`, `tqdm`, and others listed in `requirements.txt`.

Install (tooling + app):

```bash
pip install -r requirements.txt
```

---

## How to run

1. To run it, cd to the main.py in the root, then

```bash
python main.py
```

2. Follow the prompts:
   - **Pick an input file** by number (files are listed from `inputs/`).
   - **Strategy:** `1` = Dip, `2` = Trend, `3` = RSI SMA.
   - **Timeframe:** `1` = 1h, `2` = 4h, `3` = 1d (controls how history is downloaded for that run).
   - **Workers:** parallel threads (1–10) to speed up many tickers.

---

## Output files

If at least one symbol passes the strategy, results are saved as:

`outputs/<input_basename>_<strategy>_<timeframe>.csv`

If there are tickers present per strategy, the result will be saved into `/outputs`, if run a selected strategy doesn't return tickers - nothing will be saved

---

## Overview of strategies

| Strategy    | Idea (high level)                                                                                  |
| ----------- | -------------------------------------------------------------------------------------------------- |
| **Dip**     | Oversold / mean-reversion style checks (RSI, SMAs, Bollinger lower band, vs. long-term SMA).       |
| **Trend**   | EMA/ATR regime, RSI room, OBV vs. SMA, Donchian structure.                                         |
| **RSI SMA** | RSI oversold (below 30) while price is above the long SMA (200-period style from `calculate_sma`). |

Price data must have **at least 200 rows** after download; otherwise the symbol is skipped. Yahoo often returns nothing for delisted or wrong symbols—those are skipped too.

---

## Development

This repo uses NOX, the whole cfg can be found in my `nox` repo.

```bash
nox              # run all quality sessions
nox -s lint      # example: lint only
```

---
