from polygon import RESTClient

client = RESTClient("tPLBciN23cgXCJVrBHq36CLIEGWNNI0t")

details = (client.get_ticker_details
	(
	"AAPL",
	))

print(details)
