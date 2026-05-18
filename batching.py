# this file is needed for yf.download func, in order to not rate limit

import random
import time

from tqdm import tqdm


def batching(fetcher_func, all_tickers, timeframe, batch_size=100): # batch size for no 429
    combined_results = []
    total_batches = (len(all_tickers) + batch_size - 1) // batch_size

    for i in tqdm(
        range(0, len(all_tickers), batch_size), total=total_batches, desc="Batches"
    ):
        batch = all_tickers[i : i + batch_size]
        i // batch_size + 1

        batch_results = fetcher_func(batch, timeframe=timeframe)
        combined_results.extend(batch_results)

        if i + batch_size < len(all_tickers):
            time.sleep(random.uniform(2.0, 4.0))

    return combined_results
