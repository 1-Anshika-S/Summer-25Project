# adl.py

from dotenv import load_dotenv
import os
import requests
import pandas as pd
from datetime import datetime, timedelta

# —————————————————————————————————————
# 1. Load your Polygon API token
# —————————————————————————————————————
load_dotenv()
polygon_token = os.environ.get('POLYGON_TOKEN')


def load_token():
    return polygon_token


# —————————————————————————————————————
# 2. Fetch historical daily bars from Polygon
# —————————————————————————————————————
def get_historical_data(ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Returns a DataFrame with columns [date, open, high, low, close, volume]
    for the given ticker and date range (YYYY-MM-DD).
    """
    token = load_token()
    url = (
        f"https://api.polygon.io/v2/aggs/ticker/{ticker}"
        f"/range/1/day/{start_date}/{end_date}"
        f"?adjusted=true&sort=asc&limit=50000&apiKey={token}"
    )
    resp = requests.get(url)
    resp.raise_for_status()
    data = resp.json()
    if "results" not in data:
        raise ValueError(f"No data returned for {ticker}")

    df = pd.DataFrame(data["results"])
    # convert timestamp to datetime
    df["date"] = pd.to_datetime(df["t"], unit="ms")
    # rename Polygon fields to OHLCV
    df = df.rename(columns={
        "o": "open",
        "h": "high",
        "l": "low",
        "c": "close",
        "v": "volume"
    })
    return df[["date", "open", "high", "low", "close", "volume"]]


# —————————————————————————————————————
# 3. Compute CLV, MFV, and ADL
# —————————————————————————————————————
def calculate_adl(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds three new columns to df:
      - clv: Close Location Value (–1 to +1)
      - mfv: Money Flow Volume
      - adl: cumulative Accumulation/Distribution Line
    """
    # avoid division by zero on zero-range days
    range_ = df["high"] - df["low"]
    df["clv"] = ((df["close"] - df["low"]) - (df["high"] - df["close"])) / range_.replace(0, pd.NA)
    df["mfv"] = df["clv"] * df["volume"]
    df["adl"] = df["mfv"].cumsum().fillna(method="ffill").fillna(0)
    return df


# —————————————————————————————————————
# 4. Example usage
# —————————————————————————————————————
if __name__ == "__main__":
    # parameters
    ticker = "AAPL"
    end_date = datetime.today().strftime("%Y-%m-%d")
    start_date = (datetime.today() - timedelta(days=30)).strftime("%Y-%m-%d")

    # fetch, compute, and display
    df = get_historical_data(ticker, start_date, end_date)
    df = calculate_adl(df)
    print(df.tail(10))
