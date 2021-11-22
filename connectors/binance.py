from binance.client import Client
from binance.enums import SIDE_SELL, SIDE_BUY, ORDER_TYPE_MARKET
from constants.constants import API_KEY, API_SECRET
from utils.utils import get_top_symbol, get_usdt_balance, get_sized_quantity, get_lot_size

class BinanceConnector():
    client = None
    top_symbol = ''
    order_type = ORDER_TYPE_MARKET

    def __init__(self, top_symbol=None):
        self.set_client(Client(API_KEY, API_SECRET))
        self.set_top_symbol(top_symbol if top_symbol else get_top_symbol(self.client))
    
    def _post_sell_order_hook(self, bot, quantity, close):
        """ Actions that should be executed right after placing a sell order """
        modifier = bot.get_modifier()
        bot.set_quantity(quantity)
        bot.set_buy_price()
        bot.set_in_positions()
        
        if modifier:
            bot.set_modifier(modifier - 10)
                
        print('Selling positions at {}'.format(close))
        print('Current balance: {}'.format(quantity)) 

    def _post_buy_order_hook(self, bot, quantity, close):
        """ Actions that should be executed right after placing a buy order """
        bot.set_quantity(quantity)
        bot.set_buy_price(close)
        bot.set_in_positions(True)
        print('Buying positions at {}'.format(close))

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

    def create_order(self, quantity, side):
        """ Given the quantity, it executes an order of the selected type of side """
        symbol = self.top_symbol
        type = self.order_type

        try:
            return self.client.create_order(symbol=symbol, side=side, type=type, quantity=quantity)
        except Exception as error:
            print(error)
            return False

    def create_sell_order(self, bot, close):
        """ Given the bot and the close value, it places a sell order """
        order = self.create_order(bot.get_quantity(), SIDE_SELL)
                
        if order:
            self._post_sell_order_hook(bot, get_usdt_balance(self.client), close)  

    def create_buy_order(self, bot, close):
        """ Given the bot and the close value, it places a buy order """
        quantity = get_sized_quantity(bot, close)
        order = self.create_order(quantity, SIDE_BUY)
        
        if order:
            self._post_buy_order_hook(bot, quantity, close)
            return
        
        bot.modifier -= 10 if bot.modifier else 0

    def create_mock_sell_order(self, bot, close):
        """ Given the bot and the close value, it places a mocked sell order """
        quantity = bot.get_quantity() * close
        self._post_sell_order_hook(bot, quantity, close)

    def create_mock_buy_order(self, bot, close):
        """ Given the bot and the close value, it places a mocked buy order """
        quantity = bot.get_quantity() / close
        self._post_buy_order_hook(bot, quantity, close)
