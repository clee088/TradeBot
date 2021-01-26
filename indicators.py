import numpy as np
import pandas as pd
from math import sqrt

# Indicator functions used to calculate specific indicators (sma, ema, macd, hma)


# Simple moving average
def sma(data, length):
    smaData = data.rolling(window=length).mean()
    return np.round(smaData, decimals=2)

# Exponential moving average
def ema(data, length):
    prices = data.copy()
    prices.iloc[0:10] = sma(data, length)[0:10]
    emaData = prices.ewm(span=length, adjust=False).mean()
    return np.round(emaData, decimals=2)

# Moving average convergence divergence
def macd(data, fastLength=12, slowLength=26, signalLength=9):
    fast = ema(data, fastLength)
    slow = ema(data, slowLength)
    macdData = fast - slow
    signal = ema(macdData, signalLength)
    histogram = macdData - signal
    macdComplete = {
        "macd": np.round(macdData, decimals=2),
        "signal": np.round(signal, decimals=2),
        "histogram": np.round(histogram, decimals=2)
    }
    return macdComplete

# Weighted moving average
def wma(data, length):
    weights = np.arange(1, length+1)
    wmaData = data.rolling(length).apply(lambda prices: np.dot(prices, weights)/weights.sum(), raw=True)
    return np.round(wmaData, decimals=2)

# Hull moving average
def hma(data, length):
    wma1 = wma(data, int(length/2))
    wma2 = wma(data, int(length))
    wmaData = wma(2*wma1-wma2, int(sqrt(length)))
    return np.round(wmaData, decimals=2)

def hmaSlope(data, period):
    hmaSlopeData = data.rolling(34).apply(lambda price: (price[-1] - price[-period])/period, raw=True)
    return np.round(hmaSlopeData, decimals=2)