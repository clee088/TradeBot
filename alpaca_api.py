import requests, json
import config
import datetime as dt
from colorama import Fore
from zoneinfo import ZoneInfo

baseURL = config.baseURL
accountURL = f"{baseURL}/v2/account"
ordersURL = f"{baseURL}/v2/orders"
positionsURL = f"{baseURL}/v2/positions"

dataBaseURL = "https://data.alpaca.markets/v1"
barsURL = f"{dataBaseURL}/bars"
tradeURL = f"{dataBaseURL}/last/stocks"

headers = {'APCA-API-KEY-ID': config.key, 'APCA-API-SECRET-KEY': config.secretKey}

# ACCOUNT
def getAccount():
    response = requests.get(accountURL, headers=headers)
    return response.json()

# ORDERS
def createMarketOrder(symbol, qty, side, type="market", timeInForce="day"):
    data = {
        "symbol": symbol,
        "qty": qty,
        "side": side,
        "type": type,
        "time_in_force": timeInForce
    }
    response = requests.post(ordersURL, json=data, headers=headers)
    # print(response.json())
    print(f"{Fore.LIGHTYELLOW_EX}Created market order.")

def createLimitOrder(symbol, qty, side, limitPrice, type="limit", timeInForce="day"):
    data = {
        "symbol": symbol,
        "qty": qty,
        "side": side,
        "type": type,
        "time_in_force": timeInForce,
        "limit_price": limitPrice,
    }
    response = requests.post(ordersURL, json=data, headers=headers)
    # print(response.json())

def createBracketOrder(symbol, qty, type, takeProfit, stopPrice, side='buy', timeInForce='gtc', limitPrice=0.0, orderClass='bracket'):
    if type == "limit":
        data = {
            "symbol": symbol,
            "qty": qty,
            "side": side,
            "type": type,
            "time_in_force": timeInForce,
            "limit_price": limitPrice,
            "order_class": orderClass,
            "take_profit": {
                "limit_price": takeProfit
            },
            "stop_loss": {
                "stop_price": stopPrice
            }
        }
        requests.post(ordersURL, json=data, headers=headers)

    elif type == "market":
        data = {
            "symbol": symbol,
            "qty": qty,
            "side": side,
            "type": type,
            "time_in_force": timeInForce,
            "order_class": orderClass,
            "take_profit": {
                "limit_price": takeProfit
            },
            "stop_loss": {
                "stop_price": stopPrice
            }
        }
        requests.post(ordersURL, json=data, headers=headers)

    else:
        print(f"{Fore.LIGHTRED_EX}Could not place order.")
    # response = requests.post(ordersURL, json=data, headers=headers)
    # print(response.json())

def createTrailingStopOrder(symbol, qty, side="sell", type="trailing_stop", timeInForce="gtc", trailPercent=2):
    data = {
        "symbol": symbol,
        "qty": qty,
        "side": side,
        "type": type,
        "time_in_force": timeInForce,
        "trail_percent": trailPercent
    }
    response = requests.post(ordersURL, json=data, headers=headers)

def getOrders():
    response = requests.get(ordersURL, headers=headers)
    if response.json() == []:
        print(f"\n{Fore.LIGHTYELLOW_EX}No Orders.")
    else:
        print(response.json())

def cancelAllOrders():
    response = requests.delete(ordersURL, headers=headers)
    return response.json()

# POSITIONS
def getPositions(symbol=""):
    if symbol != "":
        response = requests.get(f"{positionsURL}/{symbol}", headers=headers)
    else:
        response = requests.get(positionsURL, headers=headers)
    return response.json()

def closePosition(symbol):
    response = requests.delete(f"{positionsURL}/{symbol}", headers=headers)
    # print(response.content)
    # print(f"{Fore.LIGHTYELLOW_EX}Closed {symbol} position.")

def getMarketData(symbol):
    timeframe = "1Min"
    limit = 1
    time = dt.datetime.now().astimezone(ZoneInfo('US/Eastern')) - dt.timedelta(minutes=1)
    response = requests.get(f"{barsURL}/{timeframe}?symbols={symbol}&limit={limit}&after={time}", headers=headers)
    data = response.json()
    return data

def getHistoricalMarketData(symbol, month, year):
    timeframe = "1Min"
    startDate = dt.datetime.now().astimezone(ZoneInfo('US/Eastern')).date().replace(day=1, month=month, year=year).isoformat()
    response = requests.get(f"{barsURL}/{timeframe}?symbols={symbol}&start={startDate}T09:30:00-04:00", headers=headers)
    data = response.json()
    return data

def getCurrentTradePrice(symbol):
    response = requests.get(f"{tradeURL}/{symbol}", headers=headers)
    return response.json()