from binance.client import Client
from binance.enums import SIDE_SELL, SIDE_BUY, ORDER_TYPE_MARKET
from constants import API_KEY, API_SECRET
from utils import get_top_symbol

class BinanceConnector():
    client = None
    top_symbol = ''
    order_type = ORDER_TYPE_MARKET

    def __init__(self):
        self.set_client(Client(API_KEY, API_SECRET))
        self.set_top_symbol(get_top_symbol(self.client))

    @classmethod
    def reset_top_symbol(cls, binance_connector):
        """ Recalculates the top_symbol of a connector's instance """
        client = binance_connector.get_client()
        binance_connector.set_top_symbol(get_top_symbol(client))

    def set_client(self, client=None):
        """ Setter for the client """
        self.client = client

    def get_client(self):
        """ Getter for the client """
        return self.client

    def set_top_symbol(self, top_symbol=''):
        """ Setter for the top_symbol """
        self.top_symbol = top_symbol

    def get_top_symbol(self):
        """ Getter for the top_symbol """
        return self.top_symbol

    def should_reset_top_symbol(self):
        """ Checks if the top symbol should be recalculated """
        return self.top_symbol != get_top_symbol(self.client)

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

    def create_mock_sell_order(self, bot, close):
        """ Given the bot and the close value, it places a mocked sell order """
        modifier = bot.get_modifier()
        quantity = bot.get_quantity() * close
        
        bot.set_quantity(quantity)
        bot.set_in_positions()
        
        if modifier:
            bot.set_modifier(modifier - 10)
                
        print('Selling positions at {}'.format(close))
        print('Current balance: {}'.format(quantity))       

    def create_mock_buy_order(self, bot, close):
        """ Given the bot and the close value, it places a mocked buy order """
        bot.set_quantity(bot.get_quantity() / close)
        bot.set_in_positions(True)
        print('Buying positions at {}'.format(close))
