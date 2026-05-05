import os

from csv_logic import csv_import, csv_output
from workers import worker_dip, worker_rsi_sma, worker_trend


# --- NEW: Function to let the user pick a file ---
def select_file():
    # 1. Look inside the 'inputs' folder and get all files
    folder_path = "inputs"
    files = os.listdir(folder_path)

    # 2. Show the user the files as a numbered list
    for _index, _file_name in enumerate(files):
        pass

    # 3. Ask them to pick a number
    file_choice = input(f"Select a file (1-{len(files)}): ")

    # 4. Figure out which file they picked and return the full path
    # (Subtract 1 because Python lists start counting at 0)
    selected_file_name = files[int(file_choice) - 1]
    full_path = f"{folder_path}/{selected_file_name}"

    return full_path


# -------------------------------------------------

# 1. Show the Strategy Menu

choice = input("Type 1, 2, or 3 and press Enter: ")

# 2. Route to the correct strategy
if choice == "1":
    # Call our new file menu!
    # It will pause, ask for a file, and save the path here:
    target_file = select_file()

    # Use the chosen file instead of the hardcoded one
    df = csv_import(target_file)
    fetch = worker_dip(df)
    csv_output(fetch, "outputs/dip.csv")

elif choice == "2":
    # Call our new file menu!
    # It will pause, ask for a file, and save the path here:
    target_file = select_file()

    # Use the chosen file instead of the hardcoded one
    df = csv_import(target_file)
    fetch = worker_trend(df)
    csv_output(fetch, "outputs/trend.csv")

elif choice == "3":
    # Call our new file menu!
    # It will pause, ask for a file, and save the path here:
    target_file = select_file()

    # Use the chosen file instead of the hardcoded one
    df = csv_import(target_file)
    fetch = worker_rsi_sma(df)
    csv_output(fetch, "outputs/rsi_sma.csv")

else:
    pass
