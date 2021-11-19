import websocket, json
from bot import Bot
from binance_connector import BinanceConnector

# Create the binance connector instance
binance_connector = BinanceConnector()
# Create the playground bot instance
bot = Bot(binance_connector, is_playground=True)

def on_open(ws):
    """ Prints a message confirming the connection opening """
    print('Connection stablished. Currently trading {}'.format(binance_connector.get_top_symbol()))

def on_message(ws, message):
    candle = json.loads(message)['k']
    is_candle_closed = candle['x']

    if is_candle_closed:
        close = float(candle['c'])
        bot.add_close_indicator(close)
        
        if bot.is_ready():
            rsi_indicators = bot.rsi_indicators
            roc_indicators = bot.roc_indicators
            last_rsi = rsi_indicators[-1]
            last_roc = roc_indicators[-1]
            
            print('RSI: {}. ROC: {}. Close Price: {}'.format(last_rsi, last_roc, close))

            if bot.should_sell(last_rsi):
                binance_connector.create_mock_sell_order(bot, close)
                return
            
            if not bot.in_positions:
                modifier = bot.get_modifier()
                
                if roc_indicators[-2]:
                    if bot.should_increase_modifier(last_roc, close):
                        bot.set_modifier(modifier + 10)
                    
                    if bot.should_decrease_modifier(last_roc):
                        bot.set_modifier(modifier - 10)

                if bot.should_buy(last_rsi):
                    binance_connector.create_mock_buy_order(bot, close)

    if bot.should_reset(binance_connector):       
        stop(ws)
        run(bot.get_socket())

def run(socket):
    """ Given the socket, it runs the websocket stream """
    stream = websocket.WebSocketApp(socket, on_open=on_open, on_message=on_message)
    stream.run_forever()

def stop(stream):
    """ Given a websocket stream, it stops the process and resets the bot """
    stream.keep_running = False
    BinanceConnector.reset_top_symbol(binance_connector)
    Bot.reset_bot(bot, binance_connector)

if __name__ == '__main__':
    run(bot.get_socket())