import io

import pandas as pd
import requests  # type: ignore[import-untyped] # FIX ME


OUTPUT_FILE = "inputs/lse_list.csv"


def get_wikipedia_list(url, index_name):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        resp = requests.get(url, headers=headers)
        tables = pd.read_html(io.StringIO(resp.text))
        # Usually the first or second table
        df = next(t for t in tables if any(c in t.columns for c in ["EPIC", "Ticker"]))

        ticker_col = "EPIC" if "EPIC" in df.columns else "Ticker"
        name_col = next(c for c in df.columns if c in ["Company", "Constituent"])

        data = []
        for _, row in df.iterrows():
            data.append(
                {
                    "Ticker": f"{str(row[ticker_col]).strip()}.L",
                    "Name": row[name_col],
                    "Index": index_name,
                    "Type": "Stock",
                }
            )
        return data
    except Exception:
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
        df.to_csv(OUTPUT_FILE, index=False)
    else:
        pass


if __name__ == "__main__":
    main()
