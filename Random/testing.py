#!/usr/bin/env python3
"""
callclosingprices.py

Fetches closing prices for a given stock symbol over a specified date range
using the Polygon.io API and writes them to a CSV file.
"""

from dotenv import load_dotenv
import os
import argparse
import pandas as pd
from polygon import RESTClient

# Load your POLYGON_TOKEN from a .env file
load_dotenv()
polygon_token = os.environ.get('POLYGON_TOKEN')

def load_token():
    return polygon_token

def fetch_closing_prices(symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Retrieve daily aggregate bars for `symbol` between start_date and end_date,
    then extract and return a DataFrame of dates and closing prices.
    """
    client = RESTClient(api_key=load_token())
    bars = client.get_aggregate_bars(
        symbol=symbol,
        from_date=start_date,
        to_date=end_date,
        timespan='day',
        multiplier=1,
        sort='asc',
        limit=50000,
        full_range=True
    )  # full_range=True returns a merged list of all daily bars :contentReference[oaicite:0]{index=0}

    # Normalize API response into a DataFrame
    df = pd.DataFrame(bars)
    df['date'] = pd.to_datetime(df['t'], unit='ms').dt.date
    df = df[['date', 'c']]
    df.columns = ['date', 'close']
    return df

def main():
    parser = argparse.ArgumentParser(
        description="Fetch and store closing prices for a stock symbol."
    )
    parser.add_argument("symbol", help="Stock ticker symbol, e.g., AAPL")
    parser.add_argument(
        "--start", required=True, help="Start date in YYYY-MM-DD format"
    )
    parser.add_argument(
        "--end", required=True, help="End date in YYYY-MM-DD format"
    )
    parser.add_argument(
        "--output",
        help="Output CSV file path (default: <symbol>_closing_prices_<start>_to_<end>.csv)",
    )
    args = parser.parse_args()

    df = fetch_closing_prices(args.symbol, args.start, args.end)
    output_file = args.output or f"{args.symbol}_closing_prices_{args.start}_to_{args.end}.csv"
    df.to_csv(output_file, index=False)
    print(f"Saved closing prices to {output_file}")

if __name__ == "__main__":
    main()
