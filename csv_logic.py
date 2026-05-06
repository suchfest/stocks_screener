import os

import pandas as pd


def csv_import(path):
    return pd.read_csv(path)


def csv_output(results, path):
    if not results:
        return
    df = pd.DataFrame(results)
    if "ticker" not in df.columns:
        raise ValueError
    return df.to_csv(path, index=False)


def select_file():
    # 1. Look inside the 'inputs' folder and get all files
    folder_path = "inputs"
    files = os.listdir(folder_path)

    # 2. Show the files as a numbered list
    for _index, _file_name in enumerate(files):
        # THIS IS THE FIX: Print the index (plus 1) and the file name
        pass

    # 3. Ask to pick a number
    file_choice = input(f"Select a file (1-{len(files)}): ")

    # 4. Figure out which file they picked and return the full path
    # (Subtract 1 because Python lists start counting at 0)
    selected_file_name = files[int(file_choice) - 1]
    full_path = f"{folder_path}/{selected_file_name}"

    return full_path
