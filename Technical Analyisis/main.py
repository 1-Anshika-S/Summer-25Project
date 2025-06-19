from polygon import RESTClient
from loadToken import load_token
from calculateEma import calculate_ema

ticker: str = "AAPL"
token = load_token()
client = RESTClient(token)

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

