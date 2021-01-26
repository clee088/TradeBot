import alpaca_api as api
import datetime as dt
import indicators
from time import perf_counter
from zoneinfo import ZoneInfo
from colorama import Fore
from tqdm import tqdm
import pandas as pd

class DataManager():

    def __init__(self, symbol, sqlMinutesManager, sqlHoursManager):
        self.symbol = symbol
        self.sqlMinutesManager = sqlMinutesManager
        self.sqlHoursManager = sqlHoursManager

    # Current Data -- Called when websocket receives a message -- BUG: Doesn't run on weekends/holidays
    def calculateCurrentHour(self):
        self.sqlMinutesManager.checkTable(self.symbol)
        self.sqlHoursManager.checkTable(self.symbol)
        df = self.sqlMinutesManager.createDF(self.symbol)
        df.index.name = None
        dfTime = df['time']
        times = list(map(convertStrTime, dfTime))
        today = dt.datetime.now().astimezone(ZoneInfo('US/Eastern'))
        current = times[-1]
        hour = []
        for time in times:
            if time.date() == today.date():
                if time.hour == current.hour and time.minute >= 30:
                    # print(f"1st: {time}")
                    val = df.loc[df['time'] == time.strftime('%Y-%m-%d %H:%M')]
                    hour.append(val)
                elif current.minute < 30:
                    if time.hour == current.hour and time.minute < 30 or time.hour == current.hour-1 and time.minute >= 30:
                        # print(f"2nd: {time}")
                        val = df.loc[df['time'] == time.strftime('%Y-%m-%d %H:%M')]
                        hour.append(val)
        time = hour[0]['time'].to_string(index=False).strip()
        time = convertStrTime(time).replace(minute=30)
        open = hour[0]['open'].values[0]
        highs: list[float] = [minute['high'].values[0] for minute in hour]
        high = max(highs)
        lows: list[float] = [minute['high'].values[0] for minute in hour]
        low = min(lows)
        close = hour[-1]['close'].values[0]
        volumes: list[int] = [minute['volume'].values[0] for minute in hour]
        volume = int(sum(volumes))
        try:
            self.sqlHoursManager.addData(self.symbol, time, open, high, low, close, volume)
        except Exception as error:
            print(f"ERROR ADDING DATA! -> {str(error)}")

    # Calculate indicators and add to SQL database
    def calculateHourlyIndicators(self):
        # start = perf_counter()
        self.sqlHoursManager.checkTable(self.symbol)
        # Creates hourly data frame
        df = self.sqlHoursManager.createDF(self.symbol)
        closeData = df['close']
        dfTime = df['time']
        # Indicator calculations
        macdHistogram = indicators.macd(closeData)['histogram'].values
        hmaFast = indicators.hma(closeData, 5).values
        hmaSlow = indicators.hma(closeData, 36).values
        hmaSlopeData = indicators.hma(closeData, 34).values
        hmaSlope = indicators.hmaSlope(pd.DataFrame(hmaSlopeData), 5).values
        for i in range(0, len(df), 1):
            time = dfTime[i]
            try:
                self.sqlHoursManager.addHourlyIndicators(self.symbol, time, float(macdHistogram[i]), float(hmaFast[i]), float(hmaSlow[i]), float(hmaSlope[i]))
            except Exception as error:
                print(f"ERROR ADDING INDICATOR VALUES! -> {str(error)}")
        # finish = perf_counter()
        # print(f"Added/updated indicator values in {round(finish-start, 3)} second(s).")

    # Historical Data -- Called by user
    def getHistoricalData(self, symbol, month, year):
        data = api.getHistoricalMarketData(symbol, month, year)
        bars = data[symbol]
        # Check if the time already exists in the table
        self.sqlMinutesManager.checkTable(symbol)
        for bar in tqdm(bars, bar_format="%s{l_bar}{bar}{r_bar}" % (Fore.LIGHTCYAN_EX)):
            # Variables from response
            time = convertTime(bar['t'])
            open = bar['o']
            high = bar['h']
            low = bar['l']
            close = bar['c']
            volume = bar['v']
            # Attempt to add data to table
            try:
                self.sqlMinutesManager.addData(symbol, time, open, high, low, close, volume)
            except Exception as error:
                print(f"ERROR ADDING DATA! -> {str(error)}")

    # Calculate historical data hourly bars
    def calculateHistoricalHourlyBars(self, symbol):
        self.sqlMinutesManager.checkTable(symbol)
        self.sqlHoursManager.checkTable(symbol)
        df = self.sqlMinutesManager.createDF(symbol)
        df.index.name = None
        dfTime = df['time']
        times = list(map(convertStrTime, dfTime))
        hrs = []
        # for year in tqdm(range(times[-1].year-times[0].year, -1, -1), bar_format="%s{l_bar}{bar}{r_bar}" % (Fore.LIGHTCYAN_EX)):
        #     y = times[-1].year - year
        #     print(y)
        #     for month in range(12, 0, -1):
        #         print(month)
        for day in range(times[-1].day - times[0].day, -1, -1):
            today = times[-1] - dt.timedelta(days=day)
            for i in range(9, 16, 1):
                hr = []
                for time in times:
                    # Check if time is from xx:30 to yy:29 (example: 09:30-10:29)
                    if time.year == today.year and time.month == today.month and time.day == today.day:
                        if time.hour == i and time.minute >= 30 or time.hour == i + 1 and time.minute < 30:
                            val = df.loc[df['time'] == time.strftime('%Y-%m-%d %H:%M')]
                            hr.append(val)
                hrs.append(hr)

            for hour in hrs:
                if hour != []:
                    time = hour[0]['time'].to_string(index=False).strip()
                    time = convertStrTime(time).replace(minute=30)
                    open = hour[0]['open'].values[0]
                    highs: list[float] = [minute['high'].values[0] for minute in hour]
                    high = max(highs)
                    lows: list[float] = [minute['high'].values[0] for minute in hour]
                    low = min(lows)
                    close = hour[-1]['close'].values[0]
                    volumes: list[int] = [minute['volume'].values[0] for minute in hour]
                    volume = int(sum(volumes))
                    try:
                        self.sqlHoursManager.addData(symbol, time, open, high, low, close, volume)
                    except Exception as error:
                        print(f"ERROR ADDING DATA! -> {str(error)}")


    # NOT USED
    # Get minute market data from Alpaca
    # Add data to SQL database
    def getData(self):
        print("Getting Data...")
        data = api.getMarketData(self.symbol)
        bars = data[self.symbol][0]

        # Variables from response
        time = convertTime(bars['t'])
        open = bars['o']
        high = bars['h']
        low = bars['l']
        close = bars['c']
        volume = bars['v']
        # Check if the time already exists in the table
        self.sqlMinutesManager.checkTable(self.symbol)
        # Attempt to add data to table
        try:
            self.sqlMinutesManager.addData(self.symbol, time, open, high, low, close, volume)
        except Exception as error:
            print(f"ERROR ADDING DATA! -> {str(error)}")

    def calculateHourlyBar(self):
        self.sqlMinutesManager.checkTable(self.symbol)
        self.sqlHoursManager.checkTable(self.symbol)
        today = dt.datetime.today()
        #  - dt.timedelta(days=1)
        df = self.sqlMinutesManager.createDF(self.symbol)
        df.index.name = None
        dfTime = df['time']
        times = list(map(convertStrTime, dfTime))
        hrs = []
        for i in range(9, 16, 1):
            hr = []
            for time in times:
                # Check if time is from xx:30 to yy:29 (example: 09:30-10:29)
                if time.year == today.year and time.month == today.month and time.day == today.day:
                    if time.hour == i and time.minute >= 30 or time.hour == i + 1 and time.minute < 30:
                        val = df.loc[df['time'] == time.strftime('%Y-%m-%d %H:%M')]
                        hr.append(val)
            hrs.append(hr)

        for hour in hrs:
            if hour != []:
                time = hour[0]['time'].to_string(index=False).strip()
                time = convertStrTime(time).replace(minute=30)
                open = hour[0]['open'].values[0]
                highs: list[float] = [min['high'].values[0] for min in hour]
                high = max(highs)
                lows: list[float] = [min['high'].values[0] for min in hour]
                low = min(lows)
                close = hour[-1]['close'].values[0]
                volumes: list[int] = [min['volume'].values[0] for min in hour]
                volume = int(sum(volumes))
                try:
                    self.sqlHoursManager.addData(self.symbol, time, open, high, low, close, volume)
                except Exception as error:
                    print(f"ERROR ADDING DATA! -> {str(error)}")

    # def calculateHourlyIndicators(self, symbol=""):
    #     if symbol == "":
    #         symbol = self.symbol
    #     database = self.sqlHoursManager.addHourlyIndicators(symbol)
    #     print(database)


# Convert Unix Epoch to datetime
def convertTime(timestamp):
    return dt.datetime.fromtimestamp(timestamp).astimezone(ZoneInfo('US/Eastern')).strftime('%Y-%m-%d %H:%M')

def convertStrTime(timestamp):
    return dt.datetime.strptime(timestamp, "%Y-%m-%d %H:%M")
