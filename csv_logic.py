import pandas as pd


# CSV handling


def csv_import(path):
    return pd.read_csv(path)


def csv_output(results, path):
    if not results:
        return
    df = pd.DataFrame(results)
    if "ticker" not in df.columns:
        raise ValueError
    return df.to_csv(path, index=False)
