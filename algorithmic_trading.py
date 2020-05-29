import requests
from bs4 import BeautifulSoup
import pandas as pd
from pytz import timezone
import alpaca_trade_api as tradeapi
from config import *

base_url = 'https://paper-api.alpaca.markets'
account_url = '{}/v2/account'.format(base_url)
orders_url = '{}/v2/orders'.format(base_url)

easterntz = timezone('US/Eastern')

api = tradeapi.REST(
    key_id=key_id,
    secret_key=secret_key,
    base_url=base_url
)


# function to split the list of stocks
# the API call has a max of 200 so I split into two parts
def splitList(listOfStocks):

    half = len(listOfStocks) // 2
    return listOfStocks[:half], listOfStocks[half:]

def getDate():

    now = pd.Timestamp.now(tz=easterntz)
    return now

# function to get a list of stock tickers by web scraping
def getStockTickers():

    tickers = []
    url = 'http://en.wikipedia.org/wiki/List_of_S%26P_500_companies'

    response = requests.get(url)
    site = response.content
    soup = BeautifulSoup(site, 'html.parser')
    table = soup.find('table', {'class': 'wikitable sortable'})

    for row in table.findAll('tr')[1:]:
        ticker = row.findAll('td')[0].text.rstrip()
        tickers.append(ticker)

    return splitList(tickers)


def main():
	# print(getDate())
	# print(getStockTickers())

main()
