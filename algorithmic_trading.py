import requests
import pandas as pd
import pytz
import alpaca_trade_api as tradeapi
from config import *

base_url = 'https://paper-api.alpaca.markets'
account_url = '{}/v2/account'.format(base_url)

headers = {'APCA-API-KEY-ID': key_id, 'APCA-API-SECRET-KEY': secret_key}

r = requests.get(account_url, headers=headers)

print(r.content)

