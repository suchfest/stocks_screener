from concurrent.futures import ThreadPoolExecutor

from tqdm import tqdm


def worker_logic(task_function, items_to_process, timeframe, num_workers):
    if num_workers <= 0:
        raise ValueError("Number of workers must be a positive integer.")

# processes one ticker at a time, needs try/except to handle errors
    def work_one(ticker):
        try:
            return task_function([ticker], timeframe=timeframe)
        except Exception:
            return []

    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        results = list(
            tqdm(
                executor.map(work_one, items_to_process),
                total=len(items_to_process),
            )
        )

    combined = []
    for result in results:
        if result:
            combined.extend(result)

    return combined
