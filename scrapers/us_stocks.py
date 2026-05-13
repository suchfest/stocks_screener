import time

import pandas as pd
import yfinance as yf


def get_all_nasdaq_stocks():
    """
    Get ALL stocks from NASDAQ FTP server
    This includes NASDAQ, NYSE, and AMEX exchanges
    """

    try:
        # NASDAQ-listed stocks
        nasdaq_url = "ftp://ftp.nasdaqtrader.com/symboldirectory/nasdaqlisted.txt"
        nasdaq_df = pd.read_csv(nasdaq_url, sep="|")

        # Filter out test issues and footer row
        nasdaq_df = nasdaq_df[nasdaq_df["Test Issue"] == "N"]
        nasdaq_df = nasdaq_df[nasdaq_df["Symbol"].notna()]
        nasdaq_df = nasdaq_df[nasdaq_df["Symbol"] != "Symbol"]  # Remove footer

        # NYSE and other exchange stocks
        other_url = "ftp://ftp.nasdaqtrader.com/symboldirectory/otherlisted.txt"
        other_df = pd.read_csv(other_url, sep="|")

        # Filter out test issues and footer row
        other_df = other_df[other_df["Test Issue"] == "N"]
        other_df = other_df[other_df["ACT Symbol"].notna()]
        other_df = other_df[other_df["ACT Symbol"] != "ACT Symbol"]  # Remove footer

        # Process NASDAQ stocks
        nasdaq_stocks = []
        for _, row in nasdaq_df.iterrows():
            nasdaq_stocks.append(
                {
                    "ticker": row["Symbol"],
                    "name": row["Security Name"],
                    "exchange": "NASDAQ",
                }
            )

        # Process other stocks
        other_stocks = []
        for _, row in other_df.iterrows():
            exchange_map = {
                "N": "NYSE",
                "A": "NYSE American (AMEX)",
                "P": "NYSE Arca",
                "Z": "BATS",
                "V": "IEX",
            }
            exchange_code = row.get("Exchange", "N")
            exchange = exchange_map.get(exchange_code, f"Exchange {exchange_code}")

            other_stocks.append(
                {
                    "ticker": row["ACT Symbol"],
                    "name": row["Security Name"],
                    "exchange": exchange,
                }
            )

        # Combine all stocks
        all_stocks = nasdaq_stocks + other_stocks
        df_all = pd.DataFrame(all_stocks)

        # Exchange breakdown
        # exchange_counts = df_all["exchange"].value_counts()
        # for exchange, _count in exchange_counts.items():
        #    pass

        return df_all

    except Exception:
        return None


def get_stocks_with_yfinance_info(df, sample_size=5):
    """Get detailed exchange info from yfinance for a sample"""

    sample_df = df.head(sample_size)

    for _, row in sample_df.iterrows():
        ticker = row["ticker"]
        try:
            stock = yf.Ticker(ticker)
            info = stock.info

            info.get("symbol", ticker)
            info.get("exchange", "N/A")
            info.get("longName", info.get("shortName", row["name"]))

            time.sleep(0.5)  # Rate limiting

        except Exception:
            pass


def save_to_file(df, filename="inputs/all_us_stocks.csv"):
    """Save all stocks to a CSV file"""
    try:
        import os

        # Get the directory where the script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_path = os.path.join(script_dir, filename)
        df.to_csv(output_path, index=False)
        return output_path
    except Exception:
        return None


if __name__ == "__main__":
    # Get ALL US stocks from NASDAQ FTP
    all_stocks_df = get_all_nasdaq_stocks()

    if all_stocks_df is not None:
        # Save to CSV
        save_to_file(all_stocks_df)

    else:
        pass
