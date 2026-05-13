# stocks-screener

A small Python tool that reads a list of tickers from a CSV, downloads price history from **Yahoo Finance** (via `yfinance`), and screens each symbol with one of three strategies. Matches are written to CSV under `outputs/`.

---

## What you need

- **Python 3.11+**
- Dependencies: `pandas`, `pandas-ta` (Trend / indicators), `yfinance`, `tqdm`, and others listed in `requirements.txt`.
- Internet access while the screener runs.

Install (tooling + app):

```bash
pip install -r requirements.txt
```

---

## How to run

1. Open a terminal **in the project folder** (the same directory as `main.py`).  
   Relative paths `inputs/` and `outputs/` only work if the current working directory is the repo root.

2. Put CSV files in **`inputs/`**. Each file must include a column named **`ticker`** (Yahoo symbols, e.g. `AAPL`, `SAP.DE`).

3. Start the screener:

```bash
python main.py
```

4. Follow the prompts:
   - **Pick an input file** by number (files are listed from `inputs/`).
   - **Strategy:** `1` = Dip, `2` = Trend, `3` = RSI SMA.
   - **Timeframe:** `1` = 1h, `2` = 4h, `3` = 1d (controls how history is downloaded for that run).
   - **Workers:** parallel threads (1–10) to speed up many tickers.

---

## Output files

If at least one symbol passes the strategy, results are saved as:

`outputs/<input_basename>_<strategy>_<timeframe>.csv`

Examples:

- `DE_stocks_dip_4h.csv` — Dip strategy, 4h bars, from `DE_stocks.csv`
- `all_us_stocks_trend_1d.csv` — Trend strategy, daily bars

Each row includes at least **`ticker`** (and **`timeframe`** in the current fetcher output). If nothing matches, no file is written for that run.

---

## How screening works (short)

| Strategy | Idea (high level) |
|----------|-------------------|
| **Dip** | Oversold / mean-reversion style checks (RSI, SMAs, Bollinger lower band, vs. long-term SMA). |
| **Trend** | EMA/ATR regime, RSI room, OBV vs. SMA, Donchian structure (uses pandas-ta). |
| **RSI SMA** | RSI oversold (below 30) while price is above the long SMA (200-period style from `calculate_sma`). |

Price data must have **at least 200 rows** after download; otherwise the symbol is skipped. Yahoo often returns nothing for delisted or wrong symbols—those are skipped too.

---

## Repo layout

| Path | Role |
|------|------|
| `main.py` | Prompts, runs workers, saves results. |
| `fetchers.py` | `yfinance` download by timeframe + strategy entry points. |
| `workers.py` | Thread pool + progress bar. |
| `csv_logic.py` | Read input CSV, pick file, write output CSV. |
| `strategies/` | Dip, Trend, RSI SMA rules. |
| `indicators/` | RSI, MA, Bollinger, EMA/ATR helpers. |
| `scrapers/` | Optional helpers (`us_stocks`, `xetra`, `lse`) to build ticker lists—not required to run `main.py`. |
| `tests/` | Pytest tests. |
| `noxfile.py` | Format, lint, typecheck, security, tests (`nox`). |

---

## Development

```bash
nox              # run all quality sessions
nox -s lint      # example: lint only
```

Optional: `pre-commit install` after installing requirements (see `noxfile.py` / pre-commit config if present).

---

## Notes

- **Rate limits:** Many parallel workers hammer Yahoo; if you see errors, lower worker count or add delays (not implemented here).
- **Symbols:** Use the same ticker strings as on Yahoo Finance (including exchange suffixes for non-US listings).
