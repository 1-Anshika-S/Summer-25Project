from typing import Iterator, Union, List
from http.client import HTTPResponse
from polygon import RESTClient
from polygon.rest.models import Agg
from datetime import datetime, timedelta
import pytz  # pip install pytz
from loadToken import load_token


def get_ema_list(data: list[float], period: int) -> list[float]:
    number_of_data_points: int = len(data)
    if number_of_data_points < period:
        print(number_of_data_points, period)
        raise ValueError("Not enough data points provided")

    simple_moving_average = sum(data[0:period]) / period
    alpha = 2.0 / (period + 1)
    ema_points = [simple_moving_average]
    previous_ema = simple_moving_average

    for i in range(period, number_of_data_points):
        close_price = data[i]
        ema = (close_price - previous_ema) * alpha + previous_ema
        ema_points.append(ema)
        previous_ema = ema

    return ema_points

def calculate_ema_raw(data: list[float], period: int) -> float:
    """
    Assumes data is given as a list of floats where the 0 index is the date furthest in the past and period is an int
    :return: a float representing the calculated ema
    """
    ema_list = get_ema_list(data, period)
    return ema_list[len(ema_list) - 1]

def get_list_from_aggs(
    data: Union[Iterator[Agg], HTTPResponse],
    period: int = 20
) -> list[float]:
    
    l = []
    
    for agg in data:
        l.append(agg.close)
    return l
def calculate_ema(
    data: list[float],
    period: int = 20
) -> float:
    return calculate_ema_raw(data, period)



def format_ts(ts_ms: int) -> str:
    """
    Convert a Unix-ms timestamp (int) into a human-readable string (UTC).
    """
    return datetime.utcfromtimestamp(ts_ms / 1000).strftime("%Y-%m-%d")


if __name__ == "__main__":
    # ——————————————————————————————————————————————————————————————————
    # Replace "YOUR_POLYGON_API_KEY" below with your actual Polygon.io key.
    # ——————————————————————————————————————————————————————————————————
    client = RESTClient(load_token())
    ticker = "AAPL"

    eastern_tz = pytz.timezone("US/Eastern")
    now_eastern = datetime.now(eastern_tz)
    today_et = now_eastern.date()
    end_date = today_et.strftime("%Y-%m-%d")

    lookback_days = 500
    start_date = (today_et - timedelta(days=lookback_days)).strftime("%Y-%m-%d")

    raw_aggs = client.list_aggs(
        ticker,
        1,
        "day",
        start_date,
        end_date,
        adjusted="true",
        sort="asc",
        limit=500
    )


    # Pull everything into a list so we can run calculate_ema twice:
    data_list = get_list_from_aggs(raw_aggs)
    # 3) Compute 50-day and 200-day EMAs
    ema_50 = calculate_ema(data_list, period=50)
    ema_200 = calculate_ema(data_list, period=200)

    print("50 day ema: $", ema_50)
    print("200 day ema: $", ema_200)

