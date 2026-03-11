from config.logic import valid_data, rsi_filter, fetch_price, csv_import, fetcher, filtered
import yfinance as yf
import pandas as pd
import pytest

def test_csv_imports():
    path = csv_import("inputs/fake.csv")
    assert len(path) == 3

def test_invalid_path():
    with pytest.raises(FileNotFoundError):
        csv_import("bad/path/fake.csv")


def test_small_amt_rows():
    fake_df = [1,2,3,4,5,6]
    result = valid_data(fake_df)
    assert result == False

def test_ok_amt_rows():
    fake_df = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]
    result = valid_data(fake_df)
    assert result == True

def test_rsi_filter_ok():
    first_rsi = 12.6
    result = rsi_filter(first_rsi)
    assert result == True

def test_rsi_filter_no():
    rsi = 80
    result = rsi_filter(rsi)
    assert result == False

def test_is_pd_series():
    price = fetch_price("MSFT")
    assert True == isinstance(price, pd.Series)

def test_if_ticker_valid_data():
    ticker = fetch_price("MSFT")
    lenth = valid_data(ticker)
    assert lenth == True

def test_data_not_null():
    ticker = fetch_price("MSFT")
    assert ticker.notnull().all() == True

def test_fethcer():
    df = csv_import ("inputs/fake2.csv")
    results = fetcher(df)
    assert True == isinstance(results, list)
    assert results[2]["ticker"] == "TRI"
    assert all("rsi" in result for result in results)

def test_filtered():
    df = [{"ticker": "test1", "rsi": 45.2}, {"ticker": "test2", "rsi": 28.1}]
    result = filtered(df)
    assert result[0]["ticker"] == "test2"