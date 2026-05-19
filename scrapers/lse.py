import os
import io


import pandas as pd
import requests  # type: ignore[import-untyped] # FIX ME

output_file = "inputs/lse_list.csv"



def get_wikipedia_list(url, index_name):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        resp = requests.get(url, headers=headers)
        tables = pd.read_html(io.StringIO(resp.text))
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
        project_root = os.path.dirname(os.path.abspath(__file__))
        script_route = os.path.dirname(project_root)
        output_path = os.path.join(script_route, output_file)
        parent = os.path.dirname(output_path)
        if parent:
            os.makedirs(parent, exist_ok=True)
        df.to_csv(output_path, index=False)
        
        return output_path

    else:
        pass


if __name__ == "__main__":
    main()
