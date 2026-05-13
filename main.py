from functools import partial

# Import the new helper function
from csv_logic import csv_import, process_and_save_results, select_file
from fetchers import fetcher_dip, fetcher_rsi_sma, fetcher_trend
from workers import run_with_workers


# 1. Select the target file
target_file = select_file()
df = csv_import(target_file)
tickers = df["ticker"].tolist()

# 2. Show the Strategy Menu
choice = input(
    "Strategy picker: \n Type 1 for Dip, \n Type 2 for Trend, \n Type 3 for RSI SMA \n and press Enter: "
)

# 3. Ask for Timeframe (Applies to all strategies)
timeframe_choice = input("Enter the timeframe: \n 1 - 1H, \n 2 - 4H, \n 3 - 1D: ")
if timeframe_choice == "1":
    tf_string = "1h"
elif timeframe_choice == "2":
    tf_string = "4h"
elif timeframe_choice == "3":
    tf_string = "1d"
else:
    raise ValueError("Invalid timeframe")

# 4. Ask for Workers
worker_count = int(input("Enter the number of workers (1-10): "))
if not (0 < worker_count <= 10):
    raise ValueError("Worker count must be between 0 and 10")

# 5. Route to correct strategy and run
if choice == "1":
    task = partial(fetcher_dip, timeframe=tf_string)
    fetch = run_with_workers(
        task_function=task, items_to_process=tickers, num_workers=worker_count
    )
    process_and_save_results(fetch, target_file, "dip", tf_string)

elif choice == "2":
    task = partial(fetcher_trend, timeframe=tf_string)
    fetch = run_with_workers(
        task_function=task, items_to_process=tickers, num_workers=worker_count
    )
    process_and_save_results(fetch, target_file, "trend", tf_string)

elif choice == "3":
    task = partial(fetcher_rsi_sma, timeframe=tf_string)
    fetch = run_with_workers(
        task_function=task, items_to_process=tickers, num_workers=worker_count
    )
    process_and_save_results(fetch, target_file, "rsi_sma", tf_string)

else:
    pass
