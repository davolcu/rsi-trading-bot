import pickle
from playground_constants import RSI_OVERSOLD

def get_close_indicators(name):
    """ Given the name of a file, it tries to read it and return the saved close indicators from it """
    try:
        file = open(name, 'rb')
        close_indicators = pickle.load(file)
        file.close()
        return close_indicators
    except OSError as e:
        return []

def set_close_indicators(indicators, indicator, name=''):
    """ Given a set of indicators, it adds a new one. Also if a file name has been provided, it saves the data to the file """
    indicators.append(indicator)

    if name:
        # Save the indicators to the file
        file = open(name, 'wb')
        pickle.dump(indicators, file)
        file.close()

    return indicators

def get_overbought_limit(modifier):
    """ Given the ROC modifier, it calculates the overbought limit """
    return 100 - get_oversold_limit(modifier)

def get_oversold_limit(modifier):
    """ Given the ROC modifier, it calculates the oversold limit """
    return RSI_OVERSOLD + modifier