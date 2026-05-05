from concurrent.futures import ThreadPoolExecutor

from tqdm import tqdm

from fetchers import fetcher_dip, fetcher_rsi_sma, fetcher_trend


def worker_dip(df):
    tickers = df["ticker"].tolist()
    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(tqdm(executor.map(fetcher_dip, tickers), total=len(tickers)))
    return [r for r in results if r is not None]


def worker_trend(df):
    tickers = df["ticker"].tolist()
    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(tqdm(executor.map(fetcher_trend, tickers), total=len(tickers)))
    return [r for r in results if r is not None]


def worker_rsi_sma(df):
    tickers = df["ticker"].tolist()
    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(tqdm(executor.map(fetcher_rsi_sma, tickers), total=len(tickers)))
    return [r for r in results if r is not None]
