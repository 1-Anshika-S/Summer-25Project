# calculateEma.py
# this is for anhaska songs

from typing import Iterator, Union
from http.client import HTTPResponse
from polygon import RESTClient
from polygon.rest.models import Agg
from datetime import datetime, timedelta
import pytz  # pip install pytz

def calculate_ema(
    data: Union[Iterator[Agg], HTTPResponse],
    period: int = 20
) -> list[tuple[int, float]]:
    """
    Calculate the Exponential Moving Average (EMA) for a sequence of Agg objects.

    Args:
        data: An iterator (or HTTPResponse) yielding Agg instances, each of which
              has a .close (float) and .timestamp (int).
        period: The EMA lookback period (number of bars). Default is 20.

    Returns:
        A list of tuples (timestamp, ema_value). The first (period-1) bars
        don’t produce an EMA; the first EMA is the simple moving average of the
        first `period` closes, and subsequent EMAs follow the standard formula.
    """
    # 1) Extract all closing prices and their timestamps
    closes: list[float] = []
    timestamps: list[int] = []
    for agg in data:
        closes.append(agg.close)
        timestamps.append(agg.timestamp)

    n = len(closes)
    if n < period:
        # Not enough data points to compute a single EMA
        return []

    # 2) Compute the initial SMA over the first `period` closes
    initial_sma = sum(closes[0:period]) / period

    # 3) Prepare the list that will hold (timestamp, ema) pairs
    ema_values: list[tuple[int, float]] = []
    # First EMA corresponds to the bar at index (period-1)
    ema_values.append((timestamps[period - 1], initial_sma))

    # 4) Compute the smoothing factor α = 2 / (period + 1)
    alpha = 2.0 / (period + 1)

    # 5) Iterate from the (period)th bar onward, applying the EMA formula:
    #    EMA_today = (Close_today - EMA_yesterday) * α + EMA_yesterday
    previous_ema = initial_sma
    for i in range(period, n):
        close_price = closes[i]
        ema_today = (close_price - previous_ema) * alpha + previous_ema
        ema_values.append((timestamps[i], ema_today))
        previous_ema = ema_today

    return ema_values


def format_ts(ts_ms: int) -> str:
    """
    Convert a Unix-ms timestamp (int) into a human-readable string (UTC).
    """
    return datetime.utcfromtimestamp(ts_ms / 1000).strftime("%Y-%m-%d")


if __name__ == "__main__":
    # ——————————————————————————————————————————————————————————————————
    # Replace "YOUR_POLYGON_API_KEY" below with your actual Polygon.io key.
    # ——————————————————————————————————————————————————————————————————
    client = RESTClient("4_zzTgHwqjsDwhFxO7QkQ9ofcoka_r_k")
    ticker = "AAPL"

    # ----------------------------------------------
    # 1) Compute dynamic start/end dates in Eastern Time using pytz
    # ----------------------------------------------
    eastern_tz = pytz.timezone("US/Eastern")
    now_eastern = datetime.now(eastern_tz)       # current date & time in ET
    today_et = now_eastern.date()                 # e.g. 2025-06-04 if run on June 4, 2025 ET
    end_date = today_et.strftime("%Y-%m-%d")       # "2025-06-04"

    # Subtract 400 calendar days so we cover weekends/holidays and get ≥200 trading bars
    lookback_days = 400
    start_date = (today_et - timedelta(days=lookback_days)).strftime("%Y-%m-%d")
    # e.g. if today_et is 2025-06-04, start_date becomes "2024-04-30"

    # 2) Fetch daily bars for AAPL from start_date through end_date
    raw_aggs = client.list_aggs(
        ticker,
        1,               # 1-day bars
        "day",
        start_date,      # computed above (ET)
        end_date,        # computed above (ET)
        adjusted="true",
        sort="asc",
        limit=500        # up to 500 bars
    )

    # Pull everything into a list so we can run calculate_ema twice:
    stock_list = list(raw_aggs)

    # 3) Compute 50-day and 200-day EMAs
    ema_50 = calculate_ema(stock_list, period=50)
    ema_200 = calculate_ema(stock_list, period=200)

    # 4) Print out the full EMA series for 50 and 200
    print(f"Data fetched (ET) from {start_date} through {end_date}\n")
    print("=== 50-Day EMA Series ===")
    for ts, val in ema_50:
        print(f"{format_ts(ts)}  →  {val:.2f}")
    print()
    print("=== 200-Day EMA Series ===")
    for ts, val in ema_200:
        print(f"{format_ts(ts)}  →  {val:.2f}")
    print()

    # 5) Print just the most recent EMA (i.e., the last element of each list)
    if ema_50:
        last_ts_50, last_val_50 = ema_50[-1]
        print(f"Most recent 50-day EMA as of {format_ts(last_ts_50)}: {last_val_50:.2f}")
    else:
        print("Not enough data to compute a 50-day EMA.")

    if ema_200:
        last_ts_200, last_val_200 = ema_200[-1]
        print(f"Most recent 200-day EMA as of {format_ts(last_ts_200)}: {last_val_200:.2f}")
    else:
        print("Not enough data to compute a 200-day EMA.")
