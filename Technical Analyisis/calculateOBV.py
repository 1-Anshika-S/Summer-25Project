from typing import Iterator, Union
from http.client import HTTPResponse
from polygon import RESTClient
from polygon.rest.models import Agg
from datetime import datetime, timedelta
import pytz          # pip install pytz
import statistics    # for stdev

def format_ts(ts_ms: int) -> str:
    return datetime.utcfromtimestamp(ts_ms / 1000).strftime("%Y-%m-%d")

def fetch_bars(ticker: str, lookback_days: int = 400):
    eastern = pytz.timezone("US/Eastern")
    today_et = datetime.now(eastern).date()
    start = (today_et - timedelta(days=lookback_days)).strftime("%Y-%m-%d")
    end   = today_et.strftime("%Y-%m-%d")

    client = RESTClient("4_zzTgHwqjsDwhFxO7QkQ9ofcoka_r_k")
    raw = client.list_aggs(
        ticker, 1, "day", start, end,
        adjusted="true", sort="asc", limit=500
    )
    return list(raw)  # list[Agg]

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
    ema = [None] * (period-1)
    # initial SMA → first EMA
    sma = sum(values[:period]) / period
    ema.append(sma)
    # subsequent EMAs
    for v in values[period:]:
        sma = (v - ema[-1]) * alpha + ema[-1]
        ema.append(sma)
    return ema

if __name__ == "__main__":
    ticker = "AAPL"
    bars = fetch_bars(ticker)

    # Extract parallel arrays
    closes     = [b.close   for b in bars]
    volumes    = [b.volume  for b in bars]
    timestamps = [b.timestamp for b in bars]

    # 1) Compute OBV
    obv = compute_obv(closes, volumes)

    # 2) Compute EMA on OBV
    ema_period = 20
    obv_ema = ema_list(obv, ema_period)

    # 3) Compute Bollinger Bands on OBV‐EMA
    bb_k      = 2.0
    bb_upper  = [None]*len(obv)
    bb_lower  = [None]*len(obv)
    for i in range(len(obv)):
        if i >= ema_period - 1 and obv_ema[i] is not None:
            window = obv[i+1-ema_period : i+1]
            sd = statistics.pstdev(window)
            bb_upper[i] = obv_ema[i] + bb_k * sd
            bb_lower[i] = obv_ema[i] - bb_k * sd

    # 4) Scan for signals & print table
    squeeze_lookback = 6
    signals = []  # list of (index, flag)
    print("Date       |    OBV    |  OBV_EMA  |   BB_UP   |  BB_LOW   | Signal")
    print("-"*70)
    for i in range(len(obv)):
        date = format_ts(timestamps[i])
        o    = obv[i]
        m    = obv_ema[i] if obv_ema[i] is not None else float("nan")
        u    = bb_upper[i] if bb_upper[i] is not None else float("nan")
        l    = bb_lower[i] if bb_lower[i] is not None else float("nan")

        flag = ""
        # Overbought / Oversold
        if bb_upper[i] is not None and o > bb_upper[i]:
            flag = "Overbought"
        elif bb_lower[i] is not None and o < bb_lower[i]:
            flag = "Oversold"
        # Squeeze
        if bb_upper[i] is not None and bb_lower[i] is not None and i >= squeeze_lookback - 1:
            widths = [
                (bb_upper[j] - bb_lower[j])
                for j in range(i+1-squeeze_lookback, i+1)
                if bb_upper[j] is not None and bb_lower[j] is not None
            ]
            if widths and widths[-1] == min(widths):
                flag = (flag + " & Squeeze") if flag else "Squeeze"

        print(f"{date}  | {o:10.0f} | {m:9.2f} | {u:9.2f} | {l:9.2f} | {flag or '--'}")
        if flag:
            signals.append((i, flag))

    # 5) Look-ahead price movement after each signal
    lookahead = 3
    print("\nPrice movement after signals:")
    for idx, flag in signals:
        if idx + lookahead < len(closes):
            start_p  = closes[idx]
            future_p = closes[idx + lookahead]
            delta    = future_p - start_p
            direction = "↑" if delta > 0 else ("↓" if delta < 0 else "→")
            print(
                f"{format_ts(timestamps[idx])} ({flag}): "
                f"price {direction} from {start_p:.2f} to {future_p:.2f} "
                f"in {lookahead} days"
            )
        else:
            print(
                f"{format_ts(timestamps[idx])} ({flag}): "
                f"not enough future data for {lookahead}-day lookahead"
            )