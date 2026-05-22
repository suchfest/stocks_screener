import os
from pathlib import Path
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
    inputs_path = Path("inputs")
    # all files
    files = [x for x in inputs_path.iterdir() if x.is_file()]

    # show the files as a numbered list
    print("\nAvailable files:") # type: ignore
    for index, file_obj in enumerate(files, start=1):
        print(f"{index}. {file_obj.name}") # type: ignore
    
    file_choice = int(input(f"Select a file (1-{len(files)}): "))  # type: ignore
    
    # get the selected file path object
    selected_file = files[file_choice - 1]
    
    # return it as a str
    return str(selected_file)

def save_results(results, target_file, strategy_name):
    valid_results = [r for r in results if r is not None]

    # Extract base filename
    base_filename = os.path.splitext(os.path.basename(target_file))[0]

    # Construct output path
    output_path = f"outputs/{base_filename}_{strategy_name}.csv"

    if valid_results:
        csv_output(valid_results, output_path)
    else:
        print("nothing found, nothing saved.")
