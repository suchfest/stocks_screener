from logic import (
    csv_import,
    csv_output,
    filtered,
    worker,
)


df = csv_import("inputs/FR_stocks.csv")
fetch = worker(df)
filtered_df = filtered(fetch)
output = csv_output(filtered_df, "outputs/dip.csv")
