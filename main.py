import websocket, json, talib, numpy
from constants import  SOCKET, ROC_PERIOD, RSI_PERIOD, TRADE_SYMBOL, BUY_QTY, SELL_QTY
from binance_connector import BinanceConnector
from utils import get_close_indicators, set_close_indicators, get_overbought_limit, get_oversold_limit

binance_connector = BinanceConnector()

file_name = '{}_indicators.txt'.format(TRADE_SYMBOL)
close_indicators = get_close_indicators(file_name)
in_positions = False
roc_modifier = 0

def on_message(ws, message):
    global close_indicators
    global in_positions
    global roc_modifier

    candle = json.loads(message)['k']
    is_candle_closed = candle['x']

    if is_candle_closed:
        close = float(candle['c'])
        close_indicators = set_close_indicators(close_indicators, close, file_name)

        if len(close_indicators) > RSI_PERIOD:
            np_close_indicators = numpy.array(close_indicators)
            rsi = talib.RSI(np_close_indicators, timeperiod=RSI_PERIOD)
            roc = talib.ROC(np_close_indicators, timeperiod=ROC_PERIOD)

            last_rsi = rsi[-1]
            last_roc = roc[-1]
            print('RSI: {}. ROC: {}. Close Price: {}'.format(last_rsi, last_roc, close))
            
            if last_rsi > get_overbought_limit(roc_modifier) and in_positions:
                print('Selling positions at {}'.format(close))
                order_succeeded = binance_connector.create_sell_order(SELL_QTY, TRADE_SYMBOL)

                if order_succeeded:
                    in_positions = False

                    if roc_modifier:
                        roc_modifier -= 10

                return
            
            if not in_positions:
                if roc[-2]:
                    if last_roc > 0 and close > close_indicators[-2]:
                        roc_modifier += 10
                    
                    if last_roc < 0 and roc_modifier:
                        roc_modifier -= 10

                if last_rsi < get_oversold_limit(roc_modifier):
                    print('Buying positions at {}'.format(close))
                    order_succeeded = binance_connector.create_buy_order(BUY_QTY, TRADE_SYMBOL)

                    if order_succeeded:
                        in_positions = True

ws = websocket.WebSocketApp(SOCKET, on_message=on_message)
ws.run_forever()