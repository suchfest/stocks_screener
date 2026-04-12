import pandas as pd
import requests
import io

OUTPUT_FILE = "LSE_Master_List.csv"

def get_wikipedia_list(url, index_name):
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        resp = requests.get(url, headers=headers)
        tables = pd.read_html(io.StringIO(resp.text))
        # Usually the first or second table
        df = next(t for t in tables if any(c in t.columns for c in ['EPIC', 'Ticker']))
        
        ticker_col = 'EPIC' if 'EPIC' in df.columns else 'Ticker'
        name_col = [c for c in df.columns if c in ['Company', 'Constituent']][0]
        
        data = []
        for _, row in df.iterrows():
            data.append({
                "Ticker": f"{str(row[ticker_col]).strip()}.L",
                "Name": row[name_col],
                "Index": index_name,
                "Type": "Stock"
            })
        return data
    except Exception as e:
        print(f"⚠️ Failed to scrape {index_name}: {e}")
        return []

def get_ucits_list(): #to be changed
    """
    Since LSE API is down, we target the most liquid UCITS ETFs 
    available on the LSE.
    """
    print("🌐 Collecting UCITS ETFs (High-Liquidity List)...")
    etf_data = [
        ("VUSA", "Vanguard S&P 500"), ("VUAG", "Vanguard S&P 500 Acc"),
        ("VWRL", "Vanguard All-World"), ("VWRP", "Vanguard All-World Acc"),
        ("ISF", "iShares FTSE 100"), ("VUKG", "Vanguard FTSE 100 Acc"),
        ("EQQQ", "Invesco Nasdaq 100"), ("IUSA", "iShares S&P 500"),
        ("INRG", "iShares Global Clean Energy"), ("VHYL", "Vanguard All-World High Div"),
        ("HMJR", "HSBC MSCI World"), ("PRIW", "Amundi Prime World")
    ]
    return [{"Ticker": f"{t}.L", "Name": n, "Index": "UCITS ETF", "Type": "ETF"} for t, n in etf_data]

def main():
    print("🚀 Starting Data Collection...")
    
    f100 = get_wikipedia_list("https://en.wikipedia.org/wiki/FTSE_100_Index", "FTSE 100")
    f250 = get_wikipedia_list("https://en.wikipedia.org/wiki/FTSE_250_Index", "FTSE 250")
    etfs = get_ucits_list()
    
    all_data = f100 + f250 + etfs
    
    if all_data:
        df = pd.DataFrame(all_data)
        df.to_csv(OUTPUT_FILE, index=False)
        print(f"\n✅ SUCCESS: {len(df)} rows saved to {OUTPUT_FILE}")
        print(df['Index'].value_counts())
    else:
        print("❌ No data collected.")

if __name__ == "__main__":
    main()