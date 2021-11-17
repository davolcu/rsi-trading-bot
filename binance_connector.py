from binance.client import Client
from binance.enums import SIDE_SELL, SIDE_BUY, ORDER_TYPE_MARKET
from constants import API_KEY, API_SECRET

class BinanceConector():
    client = None
    order_type=ORDER_TYPE_MARKET

    def __init__(self):
        self.client = Client(API_KEY, API_SECRET)

    def create_order(self, qty, symbol, side):
        """ Given the quantity and the currency, it executes an order of the selected type of side """
        try:
            self.client.create_order(symbol=symbol, side=side, type=self.order_type, quantity=qty)
            return True
        except Exception as e:
            print(e)
            return False
    
    def create_sell_order(self, qty, symbol):
        """ Given the quantity and the currency, it executes a selling order """
        return self.create_order(qty, symbol, SIDE_SELL)

    def create_buy_order(self, qty, symbol):
        """ Given the quantity and the currency, it executes a buying order """
        return self.create_order(qty, symbol, SIDE_BUY)
