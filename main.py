
from csv_logic import csv_import, csv_output, select_file
from fetchers import fetcher_dip, fetcher_rsi_sma, fetcher_trend
from workers import run_with_workers


# 1. Show the Strategy Menu
choice = input(
    "strategy picker: \n Type 1 for Dip, \n Type 2 for Trend, \n Type 3 for RSI SMA \n and press Enter: "
)
# 2. Route to the correct strategy
if choice == "1":
    # It will pause, ask for a file, and save the path here:
    target_file = select_file()

    worker_count = int(input("Enter the number of workers (1-10): "))
    if not (0 < worker_count <= 10):
        raise ValueError("Worker count must be between 0 and 10")
    # Use the chosen file instead of the hardcoded one
    df = csv_import(target_file)
    tickers = df["ticker"].tolist()
    fetch = run_with_workers(
        task_function=fetcher_dip, items_to_process=tickers, num_workers=worker_count
    )
    csv_output(fetch, "outputs/dip.csv")

elif choice == "2":
    # It will pause, ask for a file, and save the path here:
    target_file = select_file()
    # Use the chosen file instead of the hardcoded one
    worker_count = int(input("Enter the number of workers (1-10): "))
    if not (0 < worker_count <= 10):
        raise ValueError("Worker count must be between 0 and 10")
    # Use the chosen file instead of the hardcoded one
    df = csv_import(target_file)
    tickers = df["ticker"].tolist()
    fetch = run_with_workers(
        task_function=fetcher_trend, items_to_process=tickers, num_workers=worker_count
    )
    csv_output(fetch, "outputs/trend.csv")

elif choice == "3":
    # It will pause, ask for a file, and save the path here:
    target_file = select_file()
    # Use the chosen file instead of the hardcoded one
    worker_count = int(input("Enter the number of workers (1-10): "))
    if not (0 < worker_count <= 10):
        raise ValueError("Worker count must be between 0 and 10")
    # Use the chosen file instead of the hardcoded one
    df = csv_import(target_file)
    tickers = df["ticker"].tolist()
    fetch = run_with_workers(
        task_function=fetcher_rsi_sma,
        items_to_process=tickers,
        num_workers=worker_count,
    )
    csv_output(fetch, "outputs/rsi_sma.csv")

else:
    pass
