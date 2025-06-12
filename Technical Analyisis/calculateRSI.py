from polygon import RESTClient
from datetime import datetime, timedelta
from loadToken import load_token
import callClosingPrices


API_KEY = RESTClient(load_token()) # <--- IMPORTANT: Replace with your actual API key
TICKER = "AAPL"                 # <--- The stock ticker you want (e.g., "MSFT", "GOOG")
DAYS_BACK = 14

get_simple_closing_prices(TICKER, DAYS_BACK, RESTClient(load_token()))