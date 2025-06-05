from polygon import RESTClient

from calculateEma import calculate_ema

client = RESTClient("4_zzTgHwqjsDwhFxO7QkQ9ofcoka_r_k")
ticker: str = "AAPL"

stock_data = client.list_aggs(
    ticker,
    1,
    "day",
    "2024-01-01",
    "2025-05-05",
    adjusted="true",
    sort="asc",
    limit=120,
)

ema = calculate_ema(stock_data)
print(ema)