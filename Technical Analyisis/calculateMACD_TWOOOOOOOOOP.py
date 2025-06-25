# calculateMACD.py
# Module to load API token, fetch data, and calculate MACD indicators.
# Uses yfinance for data retrieval and dotenv for secure token loading.

from dotenv import load_dotenv
import os
import yfinance as yf
import pandas as pd

# Load environment variables from .env file
load_dotenv()
_polygon_token = os.getenv('POLYGON_TOKEN')

def load_token() -> str:
    """
    Return the Polygon API token loaded from environment variables.
    Ensure you have a .env file with POLYGON_TOKEN set.
    """
    return _polygon_token


def fetch_last_year_data(symbol: str) -> pd.DataFrame:
    """
    Fetch the last 1 year of historical price data for the given ticker symbol.

    Parameters:
        symbol (str): Ticker symbol, e.g., 'AAPL'.

    Returns:
        pd.DataFrame: DataFrame indexed by date with price columns.
    """
    # Disable progress bar to avoid red console output in PyCharm
    return yf.download(symbol, period="1y", auto_adjust=True, progress=True)


def calculate_macd(
    data: pd.DataFrame,
    short_span: int = 12,
    long_span: int = 26,
    signal_span: int = 9
) -> pd.DataFrame:
    """
    Calculate MACD line, Signal line, and Histogram, returning a new DataFrame.

    Parameters:
        data (pd.DataFrame): DataFrame with a 'Close' column.
        short_span (int): EMA span for the short term (default 12).
        long_span (int): EMA span for the long term (default 26).
        signal_span (int): EMA span for the signal line (default 9).

    Returns:
        pd.DataFrame: Original data plus columns:
            - 'MACD': MACD line values.
            - 'Signal': Signal line values.
            - 'Histogram': MACD minus Signal.
    """
    df = data.copy()
    short_ema = df['Close'].ewm(span=short_span, adjust=False).mean()
    long_ema = df['Close'].ewm(span=long_span, adjust=False).mean()
    df['MACD'] = short_ema - long_ema
    df['Signal'] = df['MACD'].ewm(span=signal_span, adjust=False).mean()
    df['Histogram'] = df['MACD'] - df['Signal']
    return df


def _test_calculate_macd():
    """
    Basic test for calculate_macd using a simple increasing series.
    """
    dates = pd.date_range('2020-01-01', periods=50)
    # Create a linear increasing 'Close' price series
    data = pd.DataFrame({'Close': range(50)}, index=dates)
    result = calculate_macd(data)
    # Ensure required columns exist
    assert all(col in result.columns for col in ['MACD', 'Signal', 'Histogram']), \
        "MACD calculation did not produce expected columns"
    # Ensure no NaNs in the output after longest EMA span
    cleaned = result.dropna()
    assert not cleaned[['MACD', 'Signal', 'Histogram']].isna().any().any(), \
        "MACD output contains NaNs where it should be fully calculated"
    print("_test_calculate_macd passed.")

if __name__ == "__main__":
    # Run tests
    _test_calculate_macd()

    # Example usage when run as a script
    symbol = input("Enter ticker symbol (e.g., AAPL): ").upper().strip()
    data = fetch_last_year_data(symbol)
    if data.empty:
        print(f"No data found for {symbol}.")
    else:
        macd_df = calculate_macd(data)
        # Extract scalar values via .iloc to avoid FutureWarning
        macd_val = macd_df['MACD'].iloc[-1]
        signal_val = macd_df['Signal'].iloc[-1]
        hist_val = macd_df['Histogram'].iloc[-1]
        diff_value = macd_val - signal_val

        # Print values without DataFrame headers
        print(f"\nLatest MACD values for {symbol}:")
        print(f"MACD: {macd_val:.6f}")
        print(f"Signal: {signal_val:.6f}")
        print(f"Histogram: {hist_val:.6f}")

        # Comparison
        if diff_value > 0:
            print(f"\nThe MACD line is above the Signal line by {diff_value:.6f}.")
        elif diff_value < 0:
            print(f"\nThe MACD line is below the Signal line by {abs(diff_value):.6f}.")
        else:
            print("\nThe MACD line and the Signal line are equal.")
