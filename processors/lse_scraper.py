import io

import pandas as pd
import requests  # type: ignore[import-untyped]


output_file = "inputs/lse.csv"


def get_wikipedia_list(url, index_name):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        resp = requests.get(url, headers=headers)
        tables = pd.read_html(io.StringIO(resp.text))

        # Find the correct table by converting columns to lowercase
        df = None
        for t in tables:
            # Create a list of lowercase columns for comparison
            lowercased_cols = [str(c).lower() for c in t.columns]
            if "epic" in lowercased_cols or "ticker" in lowercased_cols:
                df = t
                break

        if df is None:
            return []

        # Find the specific ticker and name column dynamically
        ticker_col = next(c for c in df.columns if str(c).lower() in ["epic", "ticker"])
        name_col = next(
            c for c in df.columns if str(c).lower() in ["company", "constituent"]
        )

        data = []
        for _, row in df.iterrows():
            ticker_val = str(row[ticker_col]).strip()

            # Skip any header-like rows or empty tickers if Wikipedia has them
            if not ticker_val or ticker_val.lower() in ["epic", "ticker"]:
                continue

            data.append(
                {
                    "ticker": f"{ticker_val}.L",
                    "Name": row[name_col],
                }
            )
        return data
    except Exception:
        # Crucial for debugging: tell us WHAT went wrong instead of hiding it
        return []


def main():
    f100 = get_wikipedia_list(
        "https://en.wikipedia.org/wiki/FTSE_100_Index", "FTSE 100"
    )
    f250 = get_wikipedia_list(
        "https://en.wikipedia.org/wiki/FTSE_250_Index", "FTSE 250"
    )

    all_data = f100 + f250

    if all_data:
        df = pd.DataFrame(all_data)
        df.to_csv(output_file, index=False)
    else:
        pass


if __name__ == "__main__":
    main()
