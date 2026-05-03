import pandas as pd
import yfinance as yf
import time

def get_all_nasdaq_stocks():
    """
    Get ALL stocks from NASDAQ FTP server
    This includes NASDAQ, NYSE, and AMEX exchanges
    """
    print("=" * 80)
    print("METHOD 1: NASDAQ FTP SERVER (OFFICIAL SOURCE - ALL US STOCKS)")
    print("=" * 80)
    
    try:
        # NASDAQ-listed stocks
        print("\nDownloading NASDAQ-listed stocks...")
        nasdaq_url = "ftp://ftp.nasdaqtrader.com/symboldirectory/nasdaqlisted.txt"
        nasdaq_df = pd.read_csv(nasdaq_url, sep='|')
        
        # Filter out test issues and footer row
        nasdaq_df = nasdaq_df[nasdaq_df['Test Issue'] == 'N']
        nasdaq_df = nasdaq_df[nasdaq_df['Symbol'].notna()]
        nasdaq_df = nasdaq_df[nasdaq_df['Symbol'] != 'Symbol']  # Remove footer
        
        print(f"Found {len(nasdaq_df)} NASDAQ stocks")
        
        # NYSE and other exchange stocks
        print("\nDownloading NYSE and other exchange stocks...")
        other_url = "ftp://ftp.nasdaqtrader.com/symboldirectory/otherlisted.txt"
        other_df = pd.read_csv(other_url, sep='|')
        
        # Filter out test issues and footer row
        other_df = other_df[other_df['Test Issue'] == 'N']
        other_df = other_df[other_df['ACT Symbol'].notna()]
        other_df = other_df[other_df['ACT Symbol'] != 'ACT Symbol']  # Remove footer
        
        print(f"Found {len(other_df)} NYSE/AMEX/etc stocks")
        
        # Process NASDAQ stocks
        nasdaq_stocks = []
        for _, row in nasdaq_df.iterrows():
            nasdaq_stocks.append({
                'ticker': row['Symbol'],
                'name': row['Security Name'],
                'exchange': 'NASDAQ'
            })
        
        # Process other stocks
        other_stocks = []
        for _, row in other_df.iterrows():
            exchange_map = {
                'N': 'NYSE',
                'A': 'NYSE American (AMEX)',
                'P': 'NYSE Arca',
                'Z': 'BATS',
                'V': 'IEX'
            }
            exchange_code = row.get('Exchange', 'N')
            exchange = exchange_map.get(exchange_code, f'Exchange {exchange_code}')
            
            other_stocks.append({
                'ticker': row['ACT Symbol'],
                'name': row['Security Name'],
                'exchange': exchange
            })
        
        # Combine all stocks
        all_stocks = nasdaq_stocks + other_stocks
        df_all = pd.DataFrame(all_stocks)
        
        print(f"\n{'='*80}")
        print(f"TOTAL US STOCKS: {len(df_all)}")
        print(f"{'='*80}\n")
        
        # Exchange breakdown
        print(f"\n{'='*80}")
        print("BREAKDOWN BY EXCHANGE:")
        print(f"{'='*80}")
        exchange_counts = df_all['exchange'].value_counts()
        for exchange, count in exchange_counts.items():
            print(f"{exchange:30} {count:5} stocks")
        
        return df_all
        
    except Exception as e:
        print(f"Error: {e}")
        return None

def get_stocks_with_yfinance_info(df, sample_size=5):
    """Get detailed exchange info from yfinance for a sample"""
    print(f"\n{'='*80}")
    print(f"GETTING DETAILED INFO FOR {sample_size} SAMPLE STOCKS USING YFINANCE")
    print(f"{'='*80}\n")
    
    sample_df = df.head(sample_size)
    
    for _, row in sample_df.iterrows():
        ticker = row['ticker']
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            symbol = info.get('symbol', ticker)
            exchange = info.get('exchange', 'N/A')
            name = info.get('longName', info.get('shortName', row['name']))
            
            print(f"Ticker: {symbol}")
            print(f"Exchange (from NASDAQ FTP): {row['exchange']}")
            print(f"Exchange (from yfinance): {exchange}")
            print(f"Name: {name}")
            print("-" * 80)
            
            time.sleep(0.5)  # Rate limiting
            
        except Exception as e:
            print(f"Error fetching {ticker}: {e}")
            print("-" * 80)

def save_to_file(df, filename='all_us_stocks.csv'):
    """Save all stocks to a CSV file"""
    try:
        import os
        # Get the directory where the script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_path = os.path.join(script_dir, filename)
        df.to_csv(output_path, index=False)
        print(f"\n{'='*80}")
        print(f"✅ SAVED ALL {len(df)} STOCKS TO: {output_path}")
        print(f"{'='*80}")
        return output_path
    except Exception as e:
        print(f"Error saving file: {e}")
        return None

if __name__ == "__main__":
    
    # Get ALL US stocks from NASDAQ FTP
    all_stocks_df = get_all_nasdaq_stocks()
    
    if all_stocks_df is not None:
        
        # Save to CSV
        save_to_file(all_stocks_df)
        
        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print("\n✅ This script downloaded ALL US stocks from the official NASDAQ FTP server")
        print(f"✅ Total stocks: {len(all_stocks_df)}")
        print("✅ Includes: NASDAQ, NYSE, NYSE American (AMEX), NYSE Arca, BATS, IEX")
        print("✅ Data is updated daily by NASDAQ")
        print("\n💡 You now have ticker + exchange for ALL US stocks!")
        print("💡 The CSV file contains all stocks and can be filtered/processed as needed")
    else:
        print("\n❌ Failed to download stock data")
        print("\nAlternative methods:")
        print("1. Use pytickersymbols library: pip install pytickersymbols")
        print("2. Use SEC EDGAR API: https://www.sec.gov/edgar/sec-api-documentation")
        print("3. Use yahoo-ticker-downloader (downloads ALL tickers, takes time)")