from flask import Flask
from flask_restful import Resource, Api
from flask_cors import CORS
app = Flask(__name__)
api = Api(app)
CORS(app)



class HelloWorld(Resource):
    def get(self, ticker: str):
        return {'hello': ticker}

api.add_resource(HelloWorld, '/tickers/<string:ticker>')

if __name__ == '__main__':
    app.run(
        debug=True,
        host='0.0.0.0',
        port=4999,
        threaded=True
    )
