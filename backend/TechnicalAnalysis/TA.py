import os
from polygon import RESTClient
from dotenv import load_dotenv

from callClosingPrices import get_price_data

load_dotenv()

polygon_token = os.environ.get('POLYGON_TOKEN')
client = RESTClient(polygon_token)

aapl_df = get_price_data("AAPL")
print(aapl_df)