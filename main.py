import random
import time

# Import the new helper function
from csv_logic import csv_import, process_and_save_results, select_file
from fetchers import fetcher_dip, fetcher_rsi_sma, fetcher_trend
from batching import batching

# select the target file
target_file = select_file()
df = csv_import(target_file)
all_tickers = df["ticker"].tolist()

# show the Strategy Menu
choice = input(
    "Strategy picker: \n Type 1 for Dip, \n Type 2 for Trend, \n Type 3 for RSI SMA \n and press Enter: "
)

# ask for Timeframe
timeframe_choice = input("Enter the timeframe: \n 1 - 1H, \n 2 - 4H, \n 3 - 1D: ")
if timeframe_choice == "1":
    tf_string = "1h"
elif timeframe_choice == "2":
    tf_string = "4h"
elif timeframe_choice == "3":
    tf_string = "1d"
else:
    raise ValueError("Invalid timeframe")

# avail strategies
strategy_mapping = {
    "1": (fetcher_dip,     "dip"),
    "2": (fetcher_trend,   "trend"),
    "3": (fetcher_rsi_sma, "rsi_sma"),
}

if choice not in strategy_mapping:
    raise ValueError("Invalid strategy choice")

# simplified picker from the strategy tuple above
# istead of if, elif
fetcher_func, strategy_name = strategy_mapping[choice]

 
results = batching(fetcher_func, all_tickers, tf_string)

if results:
    saved_file = f"{strategy_name}_{tf_string}"
    process_and_save_results(results, target_file, saved_file)
    print(f"\nDone. {len(results)} signals found across {len(all_tickers)} tickers, \nsaved into {saved_file}")
else:
    print(f"\nDone. 0 signals found across {len(all_tickers)} tickers, nothing saved.")
