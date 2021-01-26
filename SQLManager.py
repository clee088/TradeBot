import sqlite3
import pandas as pd
from colorama import Fore, Style

class SqlManager():

    def __init__(self, databaseName):
        print(f"Initializing SqlManager...")
        self.databaseName = databaseName
        self.connection = sqlite3.connect(f"{self.databaseName}.db", check_same_thread=False)
        self.cursor = self.connection.cursor()

    # Creates table for given symbol
    def createTable(self, symbol):
        print(f"{Fore.LIGHTYELLOW_EX}Creating table for {symbol}")
        self.cursor.execute(
            f"CREATE TABLE {symbol} (time DATE, open FLOAT, high FLOAT, low FLOAT, close FLOAT, volume INTEGER, macdHistogram FLOAT, hmaFast FLOAT, hmaSlow FLOAT, slope FLOAT, UNIQUE(time))")
        self.connection.commit()

    # Checks if table exists. If not,
    def checkTable(self, symbol):
        try:
            self.cursor.execute(f"SELECT * FROM {symbol}")
            # print(f"{symbol}, exists.")
        except:
            print(f"{Fore.LIGHTRED_EX}{symbol} does not exist.")
            self.createTable(symbol)

    # Checks if table exists without creating table
    # Called by TradeBot
    def softCheckTable(self, symbol):
        try:
            self.cursor.execute(f"SELECT * FROM {symbol}")
            print(f"{Fore.LIGHTGREEN_EX}Table {symbol} exists.")
        except:
            print(f"{Fore.LIGHTRED_EX}Table {symbol} does not exist.")

    # Checks if row has duplicate times -- should never have duplicates
    def checkRow(self, symbol, time):
        self.cursor.execute("SELECT EXISTS (SELECT * FROM '{}' WHERE TIME = '{}')".format(symbol, time))
        return self.cursor.fetchone()

    # Adds data to table named symbol and
    def addData(self, symbol, time, open, high, low, close, volume):
        # if self.checkRow(symbol, time)[0] == 0:
        #     print(f"Adding Row {time}")
        # else:
        #     print(f"Replacing Row {time}")
        self.cursor.execute(f"INSERT OR REPLACE INTO {symbol} (time, open, high, low, close, volume) VALUES (?, ?, ?, ?, ?, ?)",
                       (time, open, high, low, close, volume))
        self.connection.commit()

    # Deletes table
    def dropTable(self, symbol):
        self.cursor.execute(f"DROP TABLE {symbol}")
        self.connection.commit()
        print(f"{Fore.LIGHTRED_EX}Dropped {symbol}'s {self.databaseName} table.")

    # Create pandas data frame for data processing
    def createDF(self, tableName):
        df = pd.read_sql(f"SELECT * FROM {tableName} ORDER BY TIME ASC", self.connection)
        return df

    # Adds hourly indicator calculations to database
    def addHourlyIndicators(self, symbol, time, macdHistogram, hmaFast, hmaSlow, slope):
        self.cursor.execute("UPDATE '{}' SET macdHistogram = ?, hmaFast = ?, hmaSlow = ? , slope = ? WHERE TIME = '{}'".format(symbol, time), (macdHistogram, hmaFast, hmaSlow, slope))
        self.connection.commit()

    # Creates pandas data frame in order to calculate indicators
    def getTwoLatestRows(self, symbol):
        df = pd.read_sql(f"SELECT * FROM {symbol} ORDER BY TIME DESC LIMIT 2", self.connection)
        return df

    def listTables(self):
        self.cursor.execute(f"SELECT tbl_name FROM sqlite_master WHERE TYPE='table'")
        return self.cursor.fetchall()

    def getCount(self, symbol):
        try:
            self.cursor.execute(f"SELECT COUNT(*) FROM {symbol}")
            return self.cursor.fetchone()
        except Exception as error:
            print(f"{Fore.LIGHTRED_EX}ERROR COUNTING DATABASE! -> {str(error)}")
