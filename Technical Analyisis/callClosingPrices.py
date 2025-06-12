from polygon import RESTClient
from datetime import datetime, timedelta
from loadToken import load_token


# --- Configuration (Change these!) ---
API_KEY = RESTClient(load_token()) # <--- IMPORTANT: Replace with your actual API key
TICKER = "AAPL"                 # <--- The stock ticker you want (e.g., "MSFT", "GOOG")
DAYS_BACK = 14                  # <--- How many past days you want
# -----------------------------------

def get_simple_closing_prices(ticker, days_back, api_key):
    client = (RESTClient(load_token()))

    # Calculate the date range
    today = datetime.now().date()
    from_date = today - timedelta(days=days_back - 1) # Go back N days including today

    from_date_str = from_date.strftime("%Y-%m-%d")
    to_date_str = today.strftime("%Y-%m-%d")

    print(f"Fetching closing prices for {ticker} from {from_date_str} to {to_date_str}...")

    try:
        # Get daily aggregates (OHLC data)
        aggs = client.get_aggs(
            ticker=ticker,
            multiplier=1,      # Get 1 unit of the timespan
            timespan="day",    # Unit is 'day' (so, 1 day)
            from_=from_date_str,
            to=to_date_str,
            adjusted=True,     # Important for accurate historical prices (splits, dividends)
            sort="asc"         # Sort dates from oldest to newest
        )

        if aggs:
            print(f"\n--- {ticker} Closing Prices ({days_back} Days) ---")
            for agg in aggs:
                date = datetime.fromtimestamp(agg.timestamp / 1000).strftime("%Y-%m-%d")
                print(f"{date}: {agg.close}")
            print("------------------------------------------")
        else:
            print(f"No data found for {ticker} in the last {days_back} days.")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    get_simple_closing_prices(TICKER, DAYS_BACK, RESTClient(load_token()))