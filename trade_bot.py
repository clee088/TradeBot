import alpaca_api as api
import DataManager as DM
import SQLManager as SQL
import StreamingManager as SM
import PlotManager as PM
import TradeManager as TM
from system_text import helpText
import datetime as dt
import time
import inspect
from multiprocessing.pool import ThreadPool
import colorama
from colorama import Fore, Style
from zoneinfo import ZoneInfo
from os import system, name

class TradeBot:

    def __init__(self):
        # Colors
        colorama.init(autoreset=True)
        print(f"{Fore.YELLOW}{Style.BRIGHT}Configuring TradeBot...")
        # Initialize starting variables
        self.startTime: dt.datetime
        initStart = time.perf_counter()
        self.isRunning = True
        self.symbol = "ARKK"
        self.previousUserInput = ""
        self.userInput = ""

        print("\nInitializing SQL Databases...")
        self.sqlMinutesManager = SQL.SqlManager("minutes_data")
        self.sqlHoursManager = SQL.SqlManager("hours_data")

        print("\nInitializing Trade Manager...")
        self.tradeManager = TM.TradeManager(self.symbol, self.sqlMinutesManager, self.sqlHoursManager)

        print("\nInitializing Data Manager...")
        self.dataManager = DM.DataManager(self.symbol, self.sqlMinutesManager, self.sqlHoursManager)

        print("\nInitializing Plot Manager...")
        self.plotManager = PM.PlotManager(self.symbol, self.sqlHoursManager)

        print("\nInitializing Data Stream...")
        self.dataStreamingManager = SM.StreamingManager(self.symbol, self.sqlMinutesManager, self.dataManager, type="data")
        self.tradeStreamingManager = SM.StreamingManager(self.symbol, self.sqlMinutesManager, self.dataManager, type="trade")

        print("\nConfiguring Multiprocessing...")
        self.pool = ThreadPool(processes=3)
        self.pool.apply_async(self.streamData)
        self.pool.apply_async(self.streamTrades)
        self.pool.apply_async(self.checkHour)

        initFinish = time.perf_counter()
        print(f"\n{Fore.LIGHTGREEN_EX}{Style.BRIGHT}Initialized TradeBot in {round(initFinish - initStart, 3)} second(s)")
        print("\n=============================================")

    # Prompt user for input/command
    def prompt(self):
        self.previousUserInput = self.userInput
        self.userInput = input(f"{Fore.LIGHTBLUE_EX}Input:  ").upper()

    def listCommands(self):
        print(f'{Fore.LIGHTYELLOW_EX}{inspect.cleandoc(helpText)}')

    # SQL Functions
    def listDatabases(self):
        minutes = self.sqlMinutesManager.listTables()
        hours = self.sqlHoursManager.listTables()
        tables = f'''
        {self.sqlMinutesManager.databaseName}: {minutes}
        {self.sqlHoursManager.databaseName}: {hours}
        '''
        print(f"{Fore.LIGHTYELLOW_EX}{inspect.cleandoc(tables)}")

    def countDatabase(self, symbol):
        print(f'{Fore.LIGHTYELLOW_EX}{symbol} -> Hours: {self.sqlHoursManager.getCount(symbol)}, Minutes: {self.sqlMinutesManager.getCount(symbol)}')

    # TradeBot main run function. Keeps running until 'stop' input or keyboard interrupt
    def run(self):
        self.startTime = dt.datetime.now().astimezone(ZoneInfo('US/Eastern'))
        print(f'{Fore.LIGHTYELLOW_EX}{Style.BRIGHT}Type "HELP" for a list of commands.')
        print(f"{Fore.LIGHTYELLOW_EX}Started TradeBot at {self.startTime.strftime('%H:%M:%S %Y-%m-%d')}\n")

        while self.isRunning:

            # SYSTEM
            if self.userInput == "PREV" or self.userInput == "LAST":
                self.userInput = self.previousUserInput

            if self.userInput == "STOP":
                # Stop TradeBot
                print(f"{Fore.LIGHTRED_EX}Stopping TradeBot...")
                self.isRunning = False
                # Stop data stream
                self.dataStreamingManager.stopStream()
                self.tradeStreamingManager.stopStream()
                # Stop multiprocessing pool processes
                self.pool.terminate()
                break

            if self.userInput == "START":
                print(f"Started TradeBot at {self.startTime.strftime('%H:%M:%S %Y-%m-%d')}")

            if self.userInput == "CLEAR":
                # for windows
                if name == 'nt':
                    _ = system('cls')
                # for mac and linux(here, os.name is 'posix')
                else:
                    _ = system('clear')

            if self.userInput == "HELP":
                self.listCommands()

            if self.userInput == "UPTIME":
                print(f"{Fore.LIGHTYELLOW_EX}Uptime: {self.getUptime()}")

            # ALPACA
            if self.userInput == "CONN STREAMS":
                try:
                    self.streamTrades()
                except Exception as error:
                    print(f"{Fore.LIGHTRED_EX}Connection is already open!")
                try:
                    self.streamData()
                except Exception as error:
                    print(f"{Fore.LIGHTRED_EX}Connection is already open!")

            if self.userInput == "ACCOUNT":
                self.getAccountInfo()

            if self.userInput == "ORDERS":
                api.getOrders()

            if self.userInput == "CREATE ORDER":
                api.createMarketOrder(self.symbol, 1, "buy")
                # api.createTrailingStopOrder(symbol=self.symbol, qty=1)

            if self.userInput == "CANCEL ALL":
                api.cancelAllOrders()

            if self.userInput == "POSITIONS":
                self.getPositions()

            if self.userInput == "CLOSE POSITION":
                symbol = input("Symbol: ")
                api.closePosition(symbol)

            # SQL
            if self.userInput == "LIST DATABASES":
                self.listDatabases()

            if self.userInput == "VIEW LAST DATA":
                print(f"{Fore.LIGHTYELLOW_EX}{self.symbol.upper()} last two hourly data entries.")
                print(f"{Fore.LIGHTYELLOW_EX}{self.sqlHoursManager.getTwoLatestRows(self.symbol)}")

            if self.userInput == "COUNT DATABASE":
                symbol = input("Symbol: ").upper()
                self.countDatabase(symbol)

            if self.userInput == "CHECK TABLE":
                symbol = input("Symbol: ").upper()
                self.sqlMinutesManager.softCheckTable(symbol)

            if self.userInput == "DROP TABLE":
                symbol = input("Symbol: ").upper()
                try:
                    self.sqlMinutesManager.dropTable(symbol)
                    self.sqlHoursManager.dropTable(symbol)
                except:
                    print(f"{Fore.LIGHTRED_EX}{symbol} does not exist!")

            # DATA
            if self.userInput == "GET MARKET DATA":
                symbol = input("Symbol: ").upper()
                month = int(input("Month:   "))
                year = int(input("Year: "))
                s = time.perf_counter()
                print(f"{Fore.LIGHTYELLOW_EX}\nGetting Data...")
                self.dataManager.getHistoricalData(symbol, month, year)
                print(f"{Fore.LIGHTYELLOW_EX}\nCalculating Hourly Bars...")
                self.dataManager.calculateHistoricalHourlyBars(symbol)
                print(f"{Fore.LIGHTYELLOW_EX}\nCalculating Indicators...")
                self.dataManager.calculateHourlyIndicators()
                f = time.perf_counter()
                print(f"{Fore.LIGHTMAGENTA_EX}Finished in {round(f-s, 3)} second(s).")

            if self.userInput == "CALCULATE HOUR":
                self.dataManager.calculateCurrentHour()

            if self.userInput == "TEST INDICATOR":
                self.dataManager.calculateHourlyIndicators()
                self.tradeManager.analyzeIndicators()

            # CHARTS
            if self.userInput == "PLOT HOUR":
                self.plotManager.plotHourlyChart()

            if self.dataStreamingManager.hasTriedConnecting and self.tradeStreamingManager.hasTriedConnecting:
                self.prompt()

        # Final TradeBot Message
        print(f"{Fore.LIGHTRED_EX}{Style.BRIGHT}Stopped TradeBot -- Uptime of {self.getUptime()}.")

    def streamData(self):
        self.dataStreamingManager.streamData()

    def streamTrades(self):
        self.tradeStreamingManager.streamData()

    def getAccountInfo(self):
        info = api.getAccount()
        pdt = info['pattern_day_trader']
        pl = round(float(info['equity']) - float(info['last_equity']), 2)
        plPercent = round(pl/float(info['last_equity']) * 100, 2)
        text = f"""
        {Fore.LIGHTYELLOW_EX}Account #: {info['account_number']} <-- {Fore.LIGHTGREEN_EX if info['status'] == "ACTIVE" else Fore.LIGHTRED_EX}{info['status']}
        {Fore.LIGHTYELLOW_EX}Equity: ${info['equity']}
        {Fore.LIGHTYELLOW_EX}Buying Power: ${info['buying_power']}
        {Fore.LIGHTYELLOW_EX}Today's P/L: {Fore.LIGHTRED_EX if pl < 0 else Fore.LIGHTGREEN_EX}${pl} ({plPercent}%)
        {Fore.LIGHTYELLOW_EX}PDT: {Fore.LIGHTGREEN_EX if pdt == False else Fore.LIGHTRED_EX} {pdt}
        """
        print(inspect.cleandoc(text))

    def getPositions(self):
        cp = api.getPositions()
        if len(cp) > 0:
            for position in cp:
                symbol = position['symbol']
                qty = position['qty']
                percentGain = round(float(position['unrealized_plpc']) * 100, 2)
                print(f"{Fore.LIGHTYELLOW_EX}{symbol}: {qty} shares, {Fore.LIGHTGREEN_EX if percentGain >= 0 else Fore.LIGHTRED_EX}{percentGain}%")
        else:
            print(f"{Fore.LIGHTYELLOW_EX}No positions.")

    def checkHour(self):
        while self.isRunning:
            current = dt.datetime.now().astimezone(ZoneInfo('US/Eastern'))
            weekNumber = current.weekday()
            hour = int(current.hour)
            minute = int(current.minute)
            second = int(current.second)
            if minute != 0 and minute % 30 == 0 and second % 60 == 0 and weekNumber <= 5 \
                    and hour >= 9 and hour <= 16:
                print(f"{Fore.LIGHTMAGENTA_EX}Analyzing Indicators...")
                time.sleep(5)
                self.tradeManager.analyzeIndicators()
            # Wait for one second/run checkHour each second
            time.sleep(1)

    # Get the uptime of the TradeBot
    def getUptime(self):
        current = dt.datetime.now().astimezone(ZoneInfo('US/Eastern'))
        uptime = current - self.startTime
        return uptime
