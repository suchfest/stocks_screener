from config.logic import (
    csv_import,
    csv_output,
    filtered,
    worker,
)


df = csv_import("inputs/DE_stocks.csv")
fetch = worker(df)
filter = filtered(fetch)
output = csv_output(filter, "outputs/rsi.csv")
