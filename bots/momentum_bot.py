import numpy, talib
from constants.constants import RSI_PERIOD, ROC_PERIOD
from constants.playground_constants import TRADE_QUANTITY
from utils.utils import get_usdt_balance, get_close_indicators, get_socket, get_overbought_limit, \
    get_oversold_limit, get_lot_size

class Bot():
    socket = ''
    close_indicators = []
    quantity = 0
    modifier = 0
    lot_size = 0
    in_positions = False

    @property
    def numpy_indicators(self):
        return numpy.array(self.close_indicators)

    @property
    def rsi_indicators(self):
        return talib.RSI(self.numpy_indicators, timeperiod=RSI_PERIOD)

    @property
    def roc_indicators(self):
        return talib.ROC(self.numpy_indicators, timeperiod=ROC_PERIOD)

    def __init__(self, connector, is_playground=False):
        client = connector.get_client()
        symbol = connector.get_top_symbol()
        
        self.set_socket(get_socket(symbol))
        self.set_close_indicators(get_close_indicators(client, symbol))
        self.set_quantity(TRADE_QUANTITY if is_playground else get_usdt_balance(client))
        self.set_lot_size(get_lot_size(client, symbol))
    
    @classmethod
    def reset_bot(cls, bot, connector):
        """ Resets the default values of a bot's instance """
        client = connector.get_client()
        symbol = connector.get_top_symbol()

        bot.set_socket(get_socket(symbol))
        bot.set_close_indicators(get_close_indicators(client, symbol))
        bot.set_modifier()
        bot.set_lot_size(get_lot_size(client, symbol))
    
    def set_socket(self, socket=''):
        """ Setter for the socket """
        self.socket = socket

    def get_socket(self):
        """ Getter for the socket """
        return self.socket

    def set_close_indicators(self, close_indicators=[]):
        """ Setter for the close_indicators """
        self.close_indicators = close_indicators

    def get_close_indicators(self):
        """ Getter for the close_indicators """
        return self.close_indicators
    
    def add_close_indicator(self, close_indicator):
        """ Adds a new close indicator to the existing list """
        self.close_indicators.append(close_indicator)

    def set_quantity(self, quantity=0):
        """ Setter for the quantity """
        self.quantity = quantity

    def get_quantity(self):
        """ Getter for the quantity """
        return self.quantity

    def set_modifier(self, modifier=0):
        """ Setter for the modifier """
        self.modifier = modifier

    def get_modifier(self):
        """ Getter for the modifier """
        return self.modifier

    def set_lot_size(self, lot_size=0):
        """ Setter for the lot size """
        self.lot_size = lot_size

    def get_lot_size(self):
        """ Getter for the lot size """
        return self.lot_size

    def set_in_positions(self, in_positions=False):
        """ Setter for the in_positions """
        self.in_positions = in_positions

    def get_in_positions(self):
        """ Getter for the in_positions """
        return self.in_positions
    
    def is_ready(self):
        """ Checks if the bot is ready to start placing orders """
        return len(self.close_indicators) > RSI_PERIOD

    def should_sell(self, rsi):
        """ Checks if the bot should sell the positions """
        return rsi > get_overbought_limit(self.modifier) and self.in_positions

    def should_buy(self, rsi):
        """ Checks if the bot should buy positions """
        return rsi < get_oversold_limit(self.modifier)

    def should_increase_modifier(self, roc, close):
        """ Checks if the bot should increase the limit modifier """
        return roc >= self.roc_indicators[-2] and close > self.close_indicators[-2]

    def should_decrease_modifier(self, roc):
        """ Checks if the bot should decrease the limit modifier """
        return self.modifier and roc < self.roc_indicators[-2]

    def should_reset(self, connector):
        """ Checks if the bot should reset """
        return not self.in_positions and connector.should_reset_top_symbol()