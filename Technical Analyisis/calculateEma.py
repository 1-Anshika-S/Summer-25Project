from http.client import HTTPResponse
from typing import Iterator, Union

from polygon.rest.models import Agg


def calculate_ema(data: Union[Iterator[Agg], HTTPResponse]):
    # We calculate the ema f
    closing_points: list[float] = []
    closing_timestamps: list[int] = []
    for point in data:
        closing_points.append(point.close)
        closing_timestamps.append(point.timestamp)