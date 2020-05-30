import requests
from bs4 import BeautifulSoup
import pandas as pd
from pytz import timezone
import alpaca_trade_api as tradeapi
from config import *

base_url = 'https://paper-api.alpaca.markets'
account_url = '{}/v2/account'.format(base_url)
orders_url = '{}/v2/orders'.format(base_url)

api = tradeapi.REST(key_id=key_id, secret_key=secret_key, base_url=base_url)

# function to split the list of stocks
# the API call has a max of 200 so I split into two parts
def splitList(listOfStocks, n): 
      
    chunked_list = [listOfStocks[i:i + n] for i in range(0, len(listOfStocks), n)] 

    return chunked_list

def getDate():

    now = pd.Timestamp.now(tz=timezone('US/Eastern'))
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

    return tickers

def getPrices(listOfStocks, time):
    start_dt = time - pd.Timedelta('50 days')

    data_set = None

    tickers = splitList(listOfStocks, 200)

    for chunk in tickers:
        
        if data_set is None:
            data_set = api.get_barset(chunk, 'day', limit=5)
        
        else:
            data_set.update(api.get_barset(chunk, 'day', limit=5))

    return data_set.df

def calculateScores(price_df):

    differences = {}
    base_parameter = 10
    tableIndex = -1

    for ticker in price_df.columns.levels[0]:
        
        df = price_df[ticker]

        if len(df.close.values) > base_parameter:

            ema = df.close.ewm(span=base_parameter).mean()[tableIndex]
            
            last = df.close.values[tableIndex]
            
            difference = (last - ema) / last
            
            differences[ticker] = difference

    return sorted(differences.items(), key=lambda x : x[1])


def main():

    # stocks = getStockTickers()

    # x = splitList(stocks, 200)


    prices = getPrices(getStockTickers(), getDate())

    scores = calculateScores(prices)

    # print(scores)
	# print(getDate())
	# print(getStockTickers())

main()
