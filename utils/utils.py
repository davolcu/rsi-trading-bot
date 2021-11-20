import pandas
from constants.constants import RSI_OVERSOLD

def get_usdt_balance(client):
    """ Given the client, it extracts the quantity of usdt in the account's balance """
    balances = client.get_account()['balances']
    usdt_balance = next(balance for balance in balances if balance['asset'] == 'USDT')
    
    return float(usdt_balance['free'])

def get_top_symbol(client):
    """ Given the client, extract the top gainer symbol of cryptos """
    data_frame = pandas.DataFrame(client.get_ticker())

    # Given the data frame, let's exclude the non USDT symbol and the leverage tokens (UP/DOWN)
    data_frame = data_frame[data_frame.symbol.str.contains('USDT')]
    data_frame = data_frame[~(data_frame.symbol.str.contains('UP') | data_frame.symbol.str.contains('DOWN'))]

    # Now we turn the priceChangePercent to float and get its maximum value in the last 24 hours
    data_frame.priceChangePercent = pandas.to_numeric(data_frame.priceChangePercent, downcast='float')
    return data_frame[data_frame.priceChangePercent == data_frame.priceChangePercent.max()].symbol.values[0]

def get_socket(symbol):
    """ Given a symbol it returns the websocket url"""
    return 'wss://stream.binance.com:9443/ws/{}@kline_1m'.format(symbol.lower())

def get_close_indicators(client, symbol, interval='1m', period='1 day ago UTC'):
    """ Given a client and a symbol, it gets the candle indicators from the last day """
    candle_indicators = client.get_historical_klines(symbol, interval, period)

    # The [4] position represents the close value
    return [float(candle[4]) for candle in candle_indicators]

def get_overbought_limit(modifier):
    """ Given the ROC modifier, it calculates the overbought limit """
    return 100 - get_oversold_limit(modifier)

def get_oversold_limit(modifier):
    """ Given the ROC modifier, it calculates the oversold limit """
    return RSI_OVERSOLD + modifier

def get_real_quantity(order):
    """ Given an order, it gets the transferred quantity minus the commission """
    transaction = order['fills'][0]
    return float(transaction['qty']) - float(transaction['commission'])