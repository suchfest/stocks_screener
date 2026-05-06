import os

from csv_logic import csv_import, csv_output

# Import your workers
from workers import worker_dip  # type: ignore # FIX ME


# from workers import worker_spike

# --- THE RULEBOOK (DICTIONARY) ---
# Map the exact file name to the correct worker and output name
FILE_RULES = {
    "DE_stocks.csv": (worker_dip, "dip_output"),
    "US_stocks.csv": (worker_dip, "dip_output"),  # Can use the same worker
    # "UK_stocks.csv": (worker_spike, "spike_output")
}


# --- FILE MENU ---
def select_file():
    folder_path = "inputs"
    files = os.listdir(folder_path)

    for _index, _file_name in enumerate(files):
        pass

    file_choice = input(f"Select a file (1-{len(files)}): ")
    selected_file_name = files[int(file_choice) - 1]

    # Return BOTH the full path (to load it) AND the name (to check the rules)
    return f"{folder_path}/{selected_file_name}", selected_file_name


# ==========================================
# MAIN APP EXECUTION
# ==========================================

# 1. Ask the user for the file
target_path, file_name = select_file()

# 2. Automatically look up the worker in the rulebook
if file_name in FILE_RULES:
    # Grab the specific worker and output name for this file
    chosen_worker_function, output_name = FILE_RULES[file_name]
else:
    exit()

# 3. Run the logic
df = csv_import(target_path)

# Automatically passes the data to the correct worker
fetch = chosen_worker_function(df)

csv_output(fetch, f"outputs/{output_name}.csv")