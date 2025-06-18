# macd_calculator.py
# Python script to calculate MACD line, Signal line, and Histogram
# and report if MACD line is above the Signal line and by how much.
# Uses yfinance for data retrieval and dotenv for secure token loading.

from dotenv import load_dotenv
import os
import yfinance as yf
import pandas as pd

# Load environment variables from .env file
load_dotenv()
polygon_token = os.getenv('POLYGON_TOKEN')

def load_token():
    """
    Return the Polygon API token loaded from environment variables.
    Ensure you have a .env file with POLYGON_TOKEN set.
    """
    return polygon_token


def calculate_macd(data: pd.DataFrame, short_span: int = 12, long_span: int = 26, signal_span: int = 9):
    """
    Calculate MACD, Signal line, and Histogram for given price data.

    Parameters:
        data (pd.DataFrame): DataFrame with a 'Close' column.
        short_span (int): Span for the short-term EMA (default 12).
        long_span (int): Span for the long-term EMA (default 26).
        signal_span (int): Span for the signal line EMA (default 9).

    Returns:
        macd_line (pd.Series): The MACD line values.
        signal_line (pd.Series): The Signal line values.
        histogram (pd.Series): The MACD histogram values (MACD - Signal).
    """
    short_ema = data['Close'].ewm(span=short_span, adjust=False).mean()
    long_ema  = data['Close'].ewm(span=long_span, adjust=False).mean()
    macd_line = short_ema - long_ema
    signal_line = macd_line.ewm(span=signal_span, adjust=False).mean()
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram


def main():
    # Load Polygon token (unused in this version, but available for future enhancements)
    token = load_token()
    if not token:
        print("Warning: POLYGON_TOKEN is not set. Proceeding without a token.")

    # Ask user for ticker symbol only
    symbol = input("Enter ticker symbol (e.g., AAPL): ").upper().strip()

    # Download the last 1 year of historical data via yfinance
    data = yf.download(symbol, period="1y")

    if data.empty:
        print(f"No data found for {symbol}.")
        return

    # Calculate MACD components
    macd_line, signal_line, histogram = calculate_macd(data)

    # Attach results to DataFrame
    data['MACD'] = macd_line
    data['Signal'] = signal_line
    data['Histogram'] = histogram

    # Display the latest values
    latest = data[['MACD', 'Signal', 'Histogram']].iloc[-1]
    print(f"\nLatest MACD values for {symbol}:")
    print(latest.to_string())

    # Compare MACD line vs Signal line
    diff = latest['MACD'] - latest['Signal']
    if diff > 0:
        print(f"\nThe MACD line is above the Signal line by {diff:.6f}.")
    elif diff < 0:
        print(f"\nThe MACD line is below the Signal line by {abs(diff):.6f}.")
    else:
        print("\nThe MACD line and the Signal line are equal.")

if __name__ == "__main__":
    main()
