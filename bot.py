import websocket, json, talib, numpy
from constants import  SOCKET, RSI_PERIOD, RSI_OVERBOUGHT, RSI_OVERSOLD, TRADE_SYMBOL, BUY_QTY, SELL_QTY
from binance_connector import create_client, sell_positions, buy_positions
from utils import get_close_indicators, set_close_indicators

file_name = '{}_indicators.txt'.format(TRADE_SYMBOL)
close_indicators = get_close_indicators(file_name)
in_positions = False
client = create_client()

def on_open(ws):
    print('Connection opened')

def on_close(ws):
    print('Connection closed')

def on_message(ws, message):
    global close_indicators
    global in_positions

    candle = json.loads(message)['k']
    is_candle_closed = candle['x']

    if is_candle_closed:
        close = float(candle['c'])
        close_indicators = set_close_indicators(close_indicators, close, file_name)

        if len(close_indicators) > RSI_PERIOD:
            np_close_indicators = numpy.array(close_indicators)
            rsi = talib.RSI(np_close_indicators, timeperiod=RSI_PERIOD)
            last_rsi = rsi[-1]
            print('Last RSI calculated: {}. Last Close Price: {}'.format(last_rsi, close))

            if last_rsi > RSI_OVERBOUGHT and in_positions:
                print('Selling positions at {}'.format(close_indicators[-1]))
                order_succeeded = sell_positions(client, SELL_QTY, TRADE_SYMBOL)

                if order_succeeded:
                    in_positions = False
                    return
            
            if last_rsi < RSI_OVERSOLD and not in_positions:
                print('Buying positions at {}'.format(close_indicators[-1]))
                order_succeeded = buy_positions(client, BUY_QTY, TRADE_SYMBOL)

                if order_succeeded:
                    in_positions = True

ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()