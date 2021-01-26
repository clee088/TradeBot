import alpaca_api as api
from math import floor
from colorama import Fore

class TradeManager():

    def __init__(self, symbol, sqlMinutesManager, sqlHoursManager):
        self.symbol = symbol
        self.sqlMinutesManager = sqlMinutesManager
        self.sqlHoursManager = sqlHoursManager

    # Analyze indicator data and make trade decisions
    def analyzeIndicators(self):
        currentPosition = api.getPositions(self.symbol)
        accountInfo = api.getAccount()
        buyingPower: float = float(accountInfo['buying_power'])
        lastTrade = api.getCurrentTradePrice(self.symbol)
        lastPrice: float = float(lastTrade['last']['price'])

        df = self.sqlHoursManager.getTwoLatestRows(self.symbol)
        minutePrice = df['close'][0]
        macd = df['macdHistogram'].values
        hmaFast = df['hmaFast'].values
        hmaSlow = df['hmaSlow'].values
        slope = df['slope'].values
        # Long Positions
        macdLong = macd[1] <= 0 and macd[0] > macd[1] and macd[0] > 0
        hmaLong = hmaFast[0] > hmaFast[1]
        # Close Positions
        macdClose = macd[1] >= 0 and macd[0] < macd[1] and macd[0] < 0
        hmaClose = hmaSlow[0] < hmaSlow[1]

        slopeCheck = slope[0] > -0.12
        # Check if holding current position
        if 'code' in currentPosition.keys() and int(currentPosition['code']) == 40410000 or int(currentPosition['qty']) <= 5:
            if lastPrice <= minutePrice * 1.0025 and lastPrice >= minutePrice * 0.9975:
                qtyOfBP = floor(buyingPower * 0.5 / lastPrice)

                if macdLong and slopeCheck:
                    if qtyOfBP >= 1:
                        api.createBracketOrder(symbol=self.symbol, qty=qtyOfBP, type='limit',
                                               takeProfit=lastPrice * 1.05,
                                               stopPrice=lastPrice * 0.98, limitPrice=lastPrice)
                        print(f"{Fore.LIGHTGREEN_EX}Created limit order: MACD")
                    else:
                        print(f"{Fore.LIGHTRED_EX}Attempted order but buying power is too low: MACD")

                elif hmaLong and slopeCheck:
                    if qtyOfBP >= 1:
                        api.createBracketOrder(symbol=self.symbol, qty=qtyOfBP, type='limit',
                                               takeProfit=lastPrice * 1.05,
                                               stopPrice=lastPrice * 0.98, limitPrice=lastPrice)
                        print(f"{Fore.LIGHTGREEN_EX}Created limit order: HMA")
                    else:
                        print(f"{Fore.LIGHTRED_EX}Attempted order but buying power is too low: HMA")

        if 'qty' in currentPosition.keys() and int(currentPosition['qty']) > 0:
            if macdClose:
                api.cancelAllOrders()
                api.closePosition(self.symbol)
                print(f"{Fore.LIGHTRED_EX}Closed Position: MACD")
            elif hmaClose:
                api.cancelAllOrders()
                api.closePosition(self.symbol)
                print(f"{Fore.LIGHTRED_EX}Closed Position: HMA")

    # def analyzeStop(self):
