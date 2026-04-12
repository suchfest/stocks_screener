import pandas as pd
import requests
import io
import os

# ── HTTP mirrors of the NASDAQ FTP files (more reliable than ftp://) ─────────
NASDAQ_URL = "https://ftp.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt"
OTHER_URL  = "https://ftp.nasdaqtrader.com/dynamic/SymDir/otherlisted.txt"

# Full exchange code map (both files combined)
EXCHANGE_MAP = {
    # otherlisted.txt Exchange column
    "A": "NYSE American (AMEX)",
    "N": "NYSE",
    "P": "NYSE Arca",
    "Z": "CBOE BZX (BATS)",
    "V": "IEX",
    # nasdaqlisted.txt Market Category column
    "Q": "NASDAQ Global Select Market",
    "G": "NASDAQ Global Market",
    "S": "NASDAQ Capital Market",
}

# ETF flags per file
# nasdaqlisted:  ETF column = 'Y'
# otherlisted:   ETF column = 'Y'  (same column name)

OUTPUT_FILE = "all_us_tickers.csv"


def _fetch(url: str) -> pd.DataFrame:
    """Download pipe-delimited file over HTTPS, return raw DataFrame."""
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    # Last line is a file-creation timestamp — strip it before parsing
    lines = resp.text.splitlines()
    # Drop any line that starts with "File Creation Time" (the footer)
    lines = [l for l in lines if not l.startswith("File Creation Time")]
    content = "\n".join(lines)
    return pd.read_csv(io.StringIO(content), sep="|", dtype=str)


def get_nasdaq_listed() -> pd.DataFrame:
    """Parse nasdaqlisted.txt → clean DataFrame."""
    print("  📡 Downloading NASDAQ-listed symbols...")
    df = _fetch(NASDAQ_URL)

    # Columns: Symbol | Security Name | Market Category | Test Issue |
    #          Financial Status | Round Lot Size | ETF | NextShares
    df = df[df["Test Issue"] == "N"]          # drop test issues
    df = df[df["Symbol"].notna()]
    df = df[~df["Symbol"].str.contains(r"\$|=|\^", na=False)]  # drop warrants/rights

    df["exchange"] = df["Market Category"].map(EXCHANGE_MAP).fillna("NASDAQ")
    df["type"]     = df["ETF"].apply(lambda x: "ETF" if x == "Y" else "Stock")

    return df[["Symbol", "Security Name", "exchange", "type"]].rename(columns={
        "Symbol": "ticker",
        "Security Name": "name",
    })


def get_other_listed() -> pd.DataFrame:
    """Parse otherlisted.txt → clean DataFrame."""
    print("  📡 Downloading NYSE/AMEX/other symbols...")
    df = _fetch(OTHER_URL)

    # Columns: ACT Symbol | Security Name | Exchange | CQS Symbol |
    #          ETF | Round Lot Size | Test Issue | NASDAQ Symbol
    df = df[df["Test Issue"] == "N"]
    df = df[df["ACT Symbol"].notna()]
    df = df[~df["ACT Symbol"].str.contains(r"\$|=|\^", na=False)]

    df["exchange"] = df["Exchange"].map(EXCHANGE_MAP).fillna("Other")
    df["type"]     = df["ETF"].apply(lambda x: "ETF" if x == "Y" else "Stock")

    return df[["ACT Symbol", "Security Name", "exchange", "type"]].rename(columns={
        "ACT Symbol": "ticker",
        "Security Name": "name",
    })


def get_all_us_tickers() -> pd.DataFrame:
    print("\n" + "=" * 60)
    print("US TICKER DOWNLOADER — NASDAQ TRADER (official source)")
    print("=" * 60)

    nasdaq = get_nasdaq_listed()
    other  = get_other_listed()

    combined = pd.concat([nasdaq, other], ignore_index=True)

    # Deduplicate — NASDAQ file is authoritative for NASDAQ tickers
    combined = combined.drop_duplicates(subset=["ticker"], keep="first")

    # Drop US-listed ETFs — EU users can only trade UCITS ETFs (Xetra/Euronext)
    # Those are covered by the Frankfurt/Euronext scripts separately
    combined = combined[combined["type"] == "Stock"]

    # Remove clearly non-stock suffixes that slip through
    # e.g. AAAA+ (rights), AAAAW (warrants), AAAAU (units)
    mask = combined["ticker"].str.match(r"^[A-Z]{1,5}$")  # clean tickers only
    combined = combined[mask]

    print(f"\n{'='*60}")
    print(f"  Total tickers: {len(combined)}")
    print(f"\n  By exchange:")
    for exch, cnt in combined["exchange"].value_counts().items():
        print(f"    {exch:<35} {cnt:>5}")
    print(f"\n  By type:")
    for t, cnt in combined["type"].value_counts().items():
        print(f"    {t:<35} {cnt:>5}")
    print("=" * 60)

    return combined


def save(df: pd.DataFrame, filename: str = OUTPUT_FILE) -> str:
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
    except NameError:
        script_dir = os.getcwd()  # fallback for interactive/notebook use
    path = os.path.join(script_dir, filename)
    df.to_csv(path, index=False, encoding="utf-8")
    print(f"\n✅ Saved {len(df)} tickers → {path}")
    print(f"   Columns: {list(df.columns)}")
    print(f"   Stocks: {(df['type'] == 'Stock').sum()}")
    print(f"   ETFs:   {(df['type'] == 'ETF').sum()}")
    # Sanity check
    assert os.path.exists(path), "❌ File was not written!"
    print(f"   File size: {os.path.getsize(path):,} bytes")
    return path


if __name__ == "__main__":
    df = get_all_us_tickers()
    if df is not None and not df.empty:
        save(df)