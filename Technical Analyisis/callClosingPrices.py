import os
import datetime as dt
from functools import lru_cache

import pandas as pd
from polygon import RESTClient


# ---------- configuration ---------- #
_DEFAULT_SYMBOL   = "AAPL"          # change or pass explicitly
_PERIOD_DAYS      = 730             # rolling window length
_CACHE_FILE       = "price_data.pkl"  # local on-disk cache
_API_KEY_ENV_NAME = "POLYGON_API_KEY"
# ----------------------------------- #


def _download_polygon(symbol: str,
                      start_date: dt.date,
                      end_date: dt.date,
                      api_key: str) -> pd.DataFrame:
    """Download raw daily aggregate bars from Polygon.io."""
    client = RESTClient(api_key)
    aggs = client.get_aggs(
        symbol=symbol,
        multiplier=1,
        timespan="day",
        from_=start_date,
        to=end_date,
        adjust=True
    )

    if not aggs:
        raise ValueError(
            f"Polygon returned 0 rows for {symbol} "
            f"between {start_date} and {end_date}."
        )

    # RESTClient returns Aggregate objects – convert to dicts first
    df = pd.DataFrame(
        {
            "open":  [a.open   for a in aggs],
            "high":  [a.high   for a in aggs],
            "low":   [a.low    for a in aggs],
            "close": [a.close  for a in aggs],
            "volume":[a.volume for a in aggs],
            "vwap":  [a.vwap   for a in aggs],
            "ts":    [pd.to_datetime(a.timestamp, unit="ms") for a in aggs],
        }
    ).set_index("ts").sort_index()

    return df


@lru_cache(maxsize=4)
def get_price_data(symbol: str = _DEFAULT_SYMBOL) -> pd.DataFrame:
    """
    Return a DataFrame with the last `_PERIOD_DAYS` of daily data.

    • Reads from disk if a fresh cache exists.  
    • Otherwise → pulls from Polygon, saves to disk, and returns.
    """
    end_date   = dt.date.today()
    start_date = end_date - dt.timedelta(days=_PERIOD_DAYS)

    # 1) Try cache ----------------------------------------------------------
    if os.path.isfile(_CACHE_FILE):
        df_cached = pd.read_pickle(_CACHE_FILE)

        # Ensure cache covers the full 730-day window (accounts for weekends)
        if (
            not df_cached.empty
            and df_cached.index.min().date() <= start_date
            and df_cached.index.max().date() >= end_date - dt.timedelta(days=1)
        ):
            return df_cached.copy()  # return a safe copy

    # 2) Download fresh data ------------------------------------------------
    api_key = os.getenv(_API_KEY_ENV_NAME)
    if not api_key:
        raise EnvironmentError(
            f"Set your Polygon API key in the { _API_KEY_ENV_NAME } environment variable."
        )

    df = _download_polygon(symbol, start_date, end_date, api_key)

    # Persist for future imports
    df.to_pickle(_CACHE_FILE)

    return df


# ------------------------------------------------------------
# Expose an immediately usable DataFrame when the module loads
# ------------------------------------------------------------
price_data: pd.DataFrame = get_price_data()     # noqa: E305
