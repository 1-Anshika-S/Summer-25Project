from flask import Flask, Response
from flask_restful import Resource, Api
from flask_cors import CORS

from TechnicalAnalysis import callClosingPrices

app = Flask(__name__)
api = Api(app)
CORS(app)



supportedTickers: list[str] = ["AAPL", 'RKLB']

class HelloWorld(Resource):
    def get(self, ticker: str):
        new_ticker = ticker.upper()
        if new_ticker not in supportedTickers:
            return Response("", 404)

        closing_prices = callClosingPrices.get_price_data(new_ticker)
        return {
            'ticker': new_ticker,
            'closingPrices': closing_prices.to_string(),
        }

api.add_resource(HelloWorld, '/tickers/<string:ticker>')

if __name__ == '__main__':
    app.run(
        debug=True,
        host='0.0.0.0',
        port=4999,
        threaded=True
    )
