import os

import pandas as pd


def csv_import(path):
    return pd.read_csv(path)


def csv_output(results, path):
    if not results:
        return False
    df = pd.DataFrame(results)
    if "ticker" not in df.columns:
        raise ValueError
    df.to_csv(path, index=False)
    return True


def select_file():
    # 1. Look inside the 'inputs' folder and get all files
    folder_path = "inputs"
    files = os.listdir(folder_path)

    # 2. Show the files as a numbered list
    for _index, _file_name in enumerate(files):
        print(f"{_index + 1}. {_file_name}")

    file_choice = int(input(f"Select a file (1-{len(files)}): "))

    selected_file_name = files[int(file_choice) - 1]
    full_path = f"{folder_path}/{selected_file_name}"

    return full_path


def process_and_save_results(results, target_file, strategy_name, tf_string):
    """Filters None values, generates the filename, saves the CSV, and prints a summary."""
    valid_results = [r for r in results if r is not None]

    # Extract base filename
    base_filename = os.path.splitext(os.path.basename(target_file))[0]

    # Construct output path
    output_path = f"outputs/{base_filename}_{strategy_name}_{tf_string}.csv"

    if valid_results:
        csv_output(valid_results, output_path)
    else:
        pass
