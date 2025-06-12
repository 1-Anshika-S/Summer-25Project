from typing import Iterator, Union
from http.client import HTTPResponse
from polygon import RESTClient
from polygon.rest.models import Agg
from datetime import datetime, timedelta, timezone
from loadToken import load_token
import pytz
import statistics
import matplotlib.pyplot as plt  # for plotting

def format_ts(ts_ms: int) -> str:
    return datetime.utcfromtimestamp(ts_ms / 1000).strftime("%Y-%m-%d")

def fetch_bars(ticker: str, lookback_days: int = 400) -> list[Agg]:
    eastern = pytz.timezone("US/Eastern")
    today_et = datetime.now(eastern).date()
    start = (today_et - timedelta(days=lookback_days)).strftime("%Y-%m-%d")
    end   = today_et.strftime("%Y-%m-%d")
    client = RESTClient(load_token())
    raw = client.list_aggs(
        ticker, 1, "day",
        start, end,
        adjusted="true", sort="asc", limit=500
    )
    return list(raw)

def compute_obv(closes: list[float], volumes: list[int]) -> list[float]:
    obv = [0.0] * len(closes)
    for i in range(1, len(closes)):
        if closes[i] > closes[i-1]:
            obv[i] = obv[i-1] + volumes[i]
        elif closes[i] < closes[i-1]:
            obv[i] = obv[i-1] - volumes[i]
        else:
            obv[i] = obv[i-1]
    return obv

def ema_list(values: list[float], period: int) -> list[Union[float, None]]:
    if len(values) < period:
        return [None] * len(values)
    alpha = 2.0 / (period + 1)
    ema = [None] * (period - 1)
    sma = sum(values[:period]) / period
    ema.append(sma)
    for v in values[period:]:
        sma = (v - ema[-1]) * alpha + ema[-1]
        ema.append(sma)
    return ema

if __name__ == "__main__":
    ticker = "AAPL"
    bars   = fetch_bars(ticker)

    # extract parallel lists
    closes     = [b.close     for b in bars]
    volumes    = [b.volume    for b in bars]
    timestamps = [b.timestamp for b in bars]

    # 1) compute OBV
    obv = compute_obv(closes, volumes)

    # 2) OBV EMA + Bollinger Bands
    ema_period = 20
    obv_ema    = ema_list(obv, ema_period)
    bb_k       = 2.0
    bb_upper   = [None]*len(obv)
    bb_lower   = [None]*len(obv)
    for i in range(len(obv)):
        if i >= ema_period - 1 and obv_ema[i] is not None:
            window = obv[i+1-ema_period : i+1]
            sd     = statistics.pstdev(window)
            bb_upper[i] = obv_ema[i] + bb_k * sd
            bb_lower[i] = obv_ema[i] - bb_k * sd

    # 3) find signals
    squeeze_lookback = 6
    signals = []
    for i in range(len(obv)):
        flag = None
        if bb_upper[i] is not None and obv[i] > bb_upper[i]:
            flag = "Overbought"
        elif bb_lower[i] is not None and obv[i] < bb_lower[i]:
            flag = "Oversold"
        if (i >= squeeze_lookback - 1 and
            bb_upper[i] is not None and bb_lower[i] is not None):
            widths = [
                bb_upper[j] - bb_lower[j]
                for j in range(i+1-squeeze_lookback, i+1)
                if bb_upper[j] is not None and bb_lower[j] is not None
            ]
            if widths and widths[-1] == min(widths):
                flag = (flag + " & Squeeze") if flag else "Squeeze"
        if flag:
            signals.append((i, flag))

    # 4) prepare x-axis dates
    dates = [datetime.utcfromtimestamp(ts/1000) for ts in timestamps]

    # ------------------------------------------------------------------------
    # Plot 1: OBV + EMA + Bands + Signals
    # ------------------------------------------------------------------------
    plt.figure()
    plt.plot(dates, obv,       label="OBV")
    plt.plot(dates, obv_ema,   label=f"OBV {ema_period}-EMA")
    plt.plot(dates, bb_upper,  linestyle="--", label="Upper BB")
    plt.plot(dates, bb_lower,  linestyle="--", label="Lower BB")

    sig_dates = [dates[i] for i,_ in signals]
    sig_vals  = [obv[i]    for i,_ in signals]
    if sig_dates:
        plt.scatter(sig_dates, sig_vals,
                    marker='o', label="Signal", zorder=5)

    plt.title(f"{ticker} On-Balance Volume with {ema_period}-Period BB")
    plt.xlabel("Date")
    plt.ylabel("OBV")
    plt.legend()
    plt.tight_layout()

    # ------------------------------------------------------------------------
    # Plot 2: Close Price + Signal Markers
    # ------------------------------------------------------------------------
    plt.figure()
    plt.plot(dates, closes, label="Close Price")

    sig_price_dates = [dates[i] for i,_ in signals]
    sig_price_vals  = [closes[i] for i,_ in signals]
    if sig_price_dates:
        plt.scatter(sig_price_dates, sig_price_vals,
                    marker='x', label="Signal", zorder=5)

    plt.title(f"{ticker} Close Price with OBV Signals")
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.legend()
    plt.tight_layout()

    # ------------------------------------------------------------------------
    # Show both figures
    # ------------------------------------------------------------------------
    plt.show()
