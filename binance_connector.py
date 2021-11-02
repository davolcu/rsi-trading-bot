from binance.client import Client
from binance.enums import SIDE_SELL, SIDE_BUY, ORDER_TYPE_MARKET
from constants import API_KEY, API_SECRET

def create_client():
    """ Reads the configuration keys and returns a Binance Client instance """
    return Client(API_KEY, API_SECRET)

def sell_positions(client, qty, symbol, order_type=ORDER_TYPE_MARKET):
    """ Given the client, the quantity and the currency, it executes a selling order """
    return create_order(client, qty, symbol, SIDE_SELL, order_type)

def buy_positions(client, qty, symbol, order_type=ORDER_TYPE_MARKET):
    """ Given the client, the quantity and the currency, it executes a buying order """
    return create_order(client, qty, symbol, SIDE_BUY, order_type)

def create_order(client, qty, symbol, side, order_type=ORDER_TYPE_MARKET):
    """ Given the client, the quantity and the currency, it executes an order of the selected type of side """
    try:
        client.create_order(symbol=symbol, side=side, type=order_type, quantity=qty)
        return True
    except Exception as e:
        print(e)
        return False