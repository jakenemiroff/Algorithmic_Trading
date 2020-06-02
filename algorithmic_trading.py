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
# the API call has a max of 200 so I split into parts
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
            data_set = api.get_barset(chunk, 'day', limit=50)
        
        else:
            data_set.update(api.get_barset(chunk, 'day', limit=50))

    return data_set.df

def calculateScores(price_df):

    differences = {}
    base_parameter = 10
    tableIndex = -1

    for ticker in price_df.columns.levels[0]:
        
        df = price_df[ticker]

        if len(df.close.values) > base_parameter:

            # ema = exponential moving average
            ema = df.close.ewm(span=base_parameter).mean()[tableIndex]
            
            last = df.close.values[tableIndex]
            
            differences[ticker] = (last - ema) / last

    return sorted(differences.items(), key=lambda x : x[1])


def createOrder(prices):
    # define constants and variables
    stocks_to_buy = set()
    stocks_to_sell = set()
    orders = []
    quantity = 100
    max_holdings = 5
    account = api.get_account()
    positions = api.list_positions()
    ranked_stocks = calculateScores(prices)
    cut_off = len(ranked_stocks) // 50
    
    # take only top ten rated stocks
    # excluding stocks too expensive to buy
    for ticker, score in ranked_stocks[: cut_off]:

        price = float(prices[ticker].close.values[-1])

        if price < float(account.cash):
            stocks_to_buy.add(ticker)

    # retrieve the current positions and see how to change current portfolio
    current_holdings = {p.symbol: p for p in positions}

    tickers = set(current_holdings.keys())
    
    # update sets
    stocks_to_sell = tickers - stocks_to_buy
    stocks_to_buy = stocks_to_buy - tickers


    # put in a sell order if a stock is in current portfolio and not in the desired portfolio
    for ticker in stocks_to_sell:
        
        number_of_shares = current_holdings[ticker].qty
        orders.append({'symbol': ticker, 'qty': number_of_shares, 'side': 'sell'})

    # if current portfolio is missing stocks from the desired portfolio then put in a buy order
    maximum_buys = max_holdings - (len(positions) - len(stocks_to_sell))


    stocks_buy_list = list(stocks_to_buy)

    index = 0
    while maximum_buys > 0:

        shares = quantity // float(prices[stocks_buy_list[index]].close.values[-1])

        if shares > 0.0:
        
            orders.append({'symbol': stocks_buy_list[index], 'qty': shares, 'side': 'buy'})

            maximum_buys -= 1
        index += 1

    return orders


def main():


    prices = getPrices(getStockTickers(), getDate())

    scores = calculateScores(prices)

    order = createOrder(prices)

main()
