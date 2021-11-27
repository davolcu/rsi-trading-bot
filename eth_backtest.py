########################################################################
# This is a backtest to check the performance of the bot in the past 
# three months of the ethereum. It will compare the difference between
# using the bot and just holding the money for the time being.
########################################################################

from bots.momentum_bot import Bot
from connectors.binance import BinanceConnector
from utils.utils import get_close_indicators

# Create the binance connector instance
binance_connector = BinanceConnector(top_symbol='ETHUSDT')
# Create the playground bot instance
bot = Bot(binance_connector, is_playground=True)

def backtest():
    """ Run the backtest """
    # Start by overriding the set of indicators
    client = binance_connector.get_client()
    symbol = binance_connector.get_top_symbol()
    close_indicators = get_close_indicators(client, symbol, period='3 days ago UTC')
    bot_base_indicators = []
    
    # Extract the first day of results as the base data set
    for _ in range(1440):
        bot_base_indicators.append(close_indicators.pop(0))
    
    bot.set_close_indicators(bot_base_indicators)

    # Loop over the rest of elements of the data set to check the bot's performance
    for close in close_indicators:
        bot.add_close_indicator(close)
        
        if bot.is_ready():
            rsi_indicators = bot.rsi_indicators
            roc_indicators = bot.roc_indicators
            last_rsi = rsi_indicators[-1]
            last_roc = roc_indicators[-1]
            
            if bot.should_sell(last_rsi, close):
                binance_connector.create_mock_sell_order(bot, close)
                continue
            
            if not bot.in_positions:
                modifier = bot.get_modifier()
                
                if roc_indicators[-2]:
                    if bot.should_increase_modifier(last_roc, close):
                        bot.set_modifier(modifier + 15)
                    
                    if bot.should_decrease_modifier(last_roc):
                        bot.set_modifier(modifier - 15)

                if bot.should_buy(last_rsi):
                    binance_connector.create_mock_buy_order(bot, close)
    
    # If at the end of the loop the bot is still in positions, force the sell order
    if bot.in_positions:
        binance_connector.create_mock_sell_order(bot, 1)

    print('Final balance: {}'.format(bot.get_quantity()))

if __name__ == '__main__':
    backtest()