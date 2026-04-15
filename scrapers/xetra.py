import io

import pandas as pd
import requests  # type: ignore[import-untyped] # FIX ME


OUTPUT_FILE = "inputs/xetra_list.csv"


def get_wikipedia_list(url, index_name, suffix=".DE"):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        resp = requests.get(url, headers=headers)
        tables = pd.read_html(io.StringIO(resp.text))

        ticker_cols = ["Ticker", "Symbol", "EPIC"]
        name_cols = ["Company", "Constituent", "Name", "Stock"]

        df = next(
            t
            for t in tables
            if any(c in t.columns for c in ticker_cols)
            and any(c in t.columns for c in name_cols)
        )

        ticker_col = next(c for c in ticker_cols if c in df.columns)

        name_col = next(c for c in name_cols if c in df.columns)

        data = []
        for _, row in df.iterrows():
            ticker = str(row[ticker_col]).strip()
            if ticker and ticker != "nan" and not ticker.endswith(suffix):
                ticker = f"{ticker}{suffix}"

            data.append(
                {
                    "Ticker": ticker,
                    "Name": row[name_col.replace(suffix, "")],
                }
            )
        return data

    except Exception:
        return []


def main():
    dax = get_wikipedia_list("https://en.wikipedia.org/wiki/DAX", "DAX 40")
    mdax = get_wikipedia_list("https://en.wikipedia.org/wiki/MDAX", "MDAX 50")

    all_data = dax + mdax

    if all_data:
        df = pd.DataFrame(all_data)
        df.to_csv(OUTPUT_FILE, index=False)
    else:
        pass


if __name__ == "__main__":
    main()
