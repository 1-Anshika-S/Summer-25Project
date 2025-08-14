

import requests

SEC_DOCUMENT_URL = "https://www.sec.gov/files/company_tickers.json"

def pullTickers():
    r = requests.get(SEC_DOCUMENT_URL)
    print(r)

if __name__ == "__main__":
    pullTickers()
