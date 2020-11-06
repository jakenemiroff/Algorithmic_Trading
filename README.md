# Algorithmic Trading

This project is a simple algorithmic trading system written in python.

This program makes use of the Alpaca API and its paper trading capabilities in order to test different investing strategies without using real money.

The initial strategy I'm using (which will be adapted as time goes on), is to track the prices of several stocks that had fallen the most in value over the past 50 days, and make trades based on reasonably priced stocks.

### Running this project:

In the python file `algorithmic_trading.py`, I import config, which is a python file containing my api key_id and secret_key.

You can delete this line, and in the line where I define the api variable, simply include your own api key_id and secret_key.
