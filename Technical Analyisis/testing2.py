"I dont know what I'm doing"
"Proceed with caution"

from dotenv import load_dotenv
import os
from polygon import RESTClient
import argparse
from datetime import datetime
import pandas as pd

def load_token():
    load_dotenv()
    return os.environ.get('POLYGON_TOKEN')

def get_closing_prices(symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Fetches daily closing prices for `symbol` from Polygon between start_date and end_date (inclusive).
    Dates should be YYYY-MM-DD.
    """
    client = RESTClient(load_token())

    # Query Polygon's Aggregates endpoint
    resp = client.stocks_equities_aggregates(
        symbol=symbol,
        multiplier=1,
        timespan="day",
        from_=start_date,
        to=end_date,
        adjusted=True,
        sort="asc",
        limit=5000
    )

    # Build a DataFrame of date vs close price
    records = []
    if getattr(resp, "results", None):
        for item in resp.results:
            # t is in milliseconds since epoch
            dt = datetime.utcfromtimestamp(item["t"] / 1000).strftime("%Y-%m-%d")
            records.append({"date": dt, "close": item["c"]})

    df = pd.DataFrame(records)
    return df

def main():
    parser = argparse.ArgumentParser(
        description="Fetch historical daily closing prices for a given stock ticker via Polygon.io"
    )
    parser.add_argument("symbol", help="Stock ticker symbol, e.g. AAPL or MSFT")
    parser.add_argument(
        "--start", "-s",
        required=True,
        help="Start date (inclusive) in YYYY-MM-DD format"
    )
    parser.add_argument(
        "--end", "-e",
        required=True,
        help="End date (inclusive) in YYYY-MM-DD format"
    )
    args = parser.parse_args()

    df = get_closing_prices(args.symbol, args.start, args.end)
    if df.empty:
        print(f"No data for {args.symbol} between {args.start} and {args.end}.")
    else:
        # Pretty-print to console
        print(df.to_string(index=False))

if __name__ == "__main__":
    main()
