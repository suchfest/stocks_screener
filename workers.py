from concurrent.futures import ThreadPoolExecutor

from tqdm import tqdm


def run_with_workers(task_function, items_to_process, num_workers):
    """
    Executes a task function concurrently using a specified number of workers.
    """
    if num_workers <= 0:
        raise ValueError("Number of workers must be a positive integer.")


    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        results = list(
            tqdm(
                executor.map(task_function, items_to_process),
                total=len(items_to_process),
            )
        )

    successful_results = [result for result in results if result is not None]

    return successful_results
