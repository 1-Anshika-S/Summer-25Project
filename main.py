from polygon import RESTClient

from calculateEma import calculate_ema

client = RESTClient("lM4FCNnKsxC0zbMXO8ACcVNnBIIgTqkn")
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