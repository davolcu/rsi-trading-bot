import websocket, json, talib, numpy
from playground_constants import  SOCKET, ROC_PERIOD, RSI_PERIOD, TRADE_SYMBOL, TRADE_QUANTITY
from binance_connector import create_client
from utils import get_close_indicators, set_close_indicators, get_overbought_limit, get_oversold_limit

file_name = '{}_indicators.txt'.format(TRADE_SYMBOL)
close_indicators = get_close_indicators(file_name)
in_positions = False
client = create_client()
quantity = TRADE_QUANTITY
roc_modifier = 0

def on_open(ws):
    print('Connection opened')

def on_message(ws, message):
    global close_indicators
    global in_positions
    global quantity
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
                quantity = quantity * close
                in_positions = False

                print('Selling positions at {}'.format(close))
                print('Current balance: {}'.format(quantity))

                if roc_modifier:
                    roc_modifier -= 10

                return
            
            if not in_positions:
                if roc[-2]:
                    if last_roc > 0:
                        roc_modifier += 10
                    
                    if last_roc < 0 and roc_modifier:
                        roc_modifier -= 10

                if last_rsi < get_oversold_limit(roc_modifier):
                    print('Buying positions at {}'.format(close))
                    quantity = quantity / close
                    in_positions = True

stream = websocket.WebSocketApp(SOCKET, on_open=on_open, on_message=on_message)
stream.run_forever()