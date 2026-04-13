import os.path
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from config.logic import (
    csv_import,
    csv_output,
    fetch_price,
    fetcher,
    filtered,
    rsi_filter,
    valid_data,
    worker,
)

def test_csv_imports():
    path = csv_import("inputs/fake.csv")
    assert len(path) == 3

def test_invalid_path():
    with pytest.raises(FileNotFoundError):
        csv_import("bad/path/fake.csv")

def test_csv_output(tmp_path):
    df = [{"ticker": "test1", "rsi": 45.2}, {"ticker": "test2", "rsi": 28.1}]
    path = tmp_path / "output.csv"
    file = csv_output(df, path)
    assert os.path.exists(path) == True

def test_wrong_df(tmp_path):
    df = [{"column": "test1", "rsi": 45.2}, {"column": "test2", "rsi": 28.1}]
    path = tmp_path / "output.csv"
    #file = csv_output(df, path)
    with pytest.raises(ValueError):
        csv_output(df, path)

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


@patch("config.logic.yf.Ticker")
def test_fetch_price_returns_usable_close_series(mock_ticker_cls):
    """Single check for fetch_price shape: Series, enough rows, no nulls (mocked, no network)."""
    closes = pd.Series(
        range(100, 115),
        index=pd.date_range("2024-01-01", periods=15, freq="D"),
        name="Close",
    )
    mock_hist = closes.to_frame()
    mock_inst = MagicMock()
    mock_inst.history.return_value = mock_hist
    mock_ticker_cls.return_value = mock_inst

    price = fetch_price("MSFT")

    assert isinstance(price, pd.Series)
    assert valid_data(price) is True
    assert price.notnull().all()


def test_fetcher_success():
    """Test fetcher returns correct data when valid prices are found."""
    ticker = "AAPL"
    mock_prices = [100, 101, 102]
    mock_rsi_series = pd.Series([30, 40, 55.5])

    with patch("config.logic.fetch_price", return_value=mock_prices), \
         patch("config.logic.valid_data", return_value=True), \
         patch("config.logic.calculate_rsi", return_value=mock_rsi_series):
        
        result = fetcher(ticker)
        
        assert result == {"ticker": "AAPL", "rsi": 55.5}
        assert isinstance(result["rsi"], float)

def test_fetcher_invalid_data():
    """Test fetcher returns None if data is invalid."""
    with patch("config.logic.fetch_price", return_value=[]), \
         patch("config.logic.valid_data", return_value=False):
        
        result = fetcher("INVALID")
        assert result is None


def test_worker_filters_none_values():
    """Test worker aggregates results and filters out None returns."""
    # Setup mock dataframe
    df = pd.DataFrame({"ticker": ["AAPL", "GOOGL", "TSLA"]})
    
    # Mocking fetcher to return a mix of data and None
    mock_responses = [
        {"ticker": "AAPL", "rsi": 50.0},
        None,
        {"ticker": "TSLA", "rsi": 70.0}
    ]

    with patch("config.logic.fetcher", side_effect=mock_responses):
        result = worker(df)
        
        # Should only contain the 2 valid responses
        assert len(result) == 2
        assert result[0]["ticker"] == "AAPL"
        assert result[1]["ticker"] == "TSLA"

@patch("config.logic.ThreadPoolExecutor")
def test_worker_thread_config(mock_executor,):
    """Verifies the worker actually attempts to use 5 threads."""
    df = pd.DataFrame({"ticker": ["AAPL"]})
    
    # We just want to see if the executor was initialized correctly
    worker(df)
    
    # Check if ThreadPoolExecutor was called with max_workers=5
    mock_executor.assert_called_once_with(max_workers=5)

def test_filtered():
    df = [{"ticker": "test1", "rsi": 45.2}, {"ticker": "test2", "rsi": 28.1}]
    result = filtered(df)
    assert result[0]["ticker"] == "test2"