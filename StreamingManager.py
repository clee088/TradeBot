import json, websocket, config
import DataManager as DM
from colorama import Fore, Style
import inspect

class StreamingManager():

    def __init__(self, symbol, sqlManager, dataManager, type):
        print(f"Initializing {'Trade Streaming Manager' if type == 'trade' else 'Data Streaming Manager'}...")
        self.hasTriedConnecting = False
        self.symbol = symbol
        self.sqlManager = sqlManager
        self.dataManager = dataManager
        self.type = type
        self.socket = f"wss://{config.baseSocket}/stream" if self.type == "trade" else "wss://data.alpaca.markets/stream"
        self.ws = websocket.WebSocketApp(self.socket, on_open=self.onOpen, on_close=self.onClose,
                                         on_message=self.onMessage)

    def streamData(self):
        # sampleDataMessage = '{"stream":"AM.PRNT","data":{"ev":"AM","T":"PRNT","v":260,"av":20276,"op":36.75,"vw":38.12,"o":38.12,"c":38.12,"h":38.12,"l":38.12,"a":37.9152,"s":1610649300000,"e":1610649360000}}'
        # self.onMessage(sampleDataMessage)
        self.ws.run_forever()

    def stopStream(self):
        self.ws.close()

    def onOpen(self):
        nl = "\n"
        print(f'{nl if self.type == "data" else ""}{Fore.LIGHTGREEN_EX}Opened websocket connection to {"TRADE STREAM" if self.type == "trade" else "DATA STREAM"}.')
        authData = {
            "action": "authenticate",
            "data": {
                "key_id": config.key,
                "secret_key": config.secretKey
            }
        }
        self.ws.send(json.dumps(authData))
        listenData = {"action": "listen", "data": {"streams": ["trade_updates"]}} if self.type == "trade" else {"action": "listen", "data": {"streams": [f"AM.{self.symbol}"]}}
        self.ws.send(json.dumps(listenData))

    def onClose(self):
        print(f'{Fore.LIGHTRED_EX}Closed websocket connection to {"TRADE STREAM" if self.type == "trade" else "DATA STREAM"}.')
        self.hasTriedConnecting = True

    def onMessage(self, message):
        jsonData = json.loads(message)
        stream = jsonData['stream']
        data = jsonData['data']
        keys = data.keys()
        if "error" in keys:
            print(f"{Fore.LIGHTRED_EX}ERROR: -> {data['error']}!")

        if "status" in keys:
            if data['status'] == "authorized":
                print(f'{Fore.LIGHTGREEN_EX}Authorized connection to {"TRADE STREAM" if self.type == "trade" else "DATA STREAM"}.')
            elif data['status'] == "unauthorized":
                print(f"{Fore.LIGHTRED_EX}Unable to authorize connection.")
            self.hasTriedConnecting = True

        if self.type == "trade":
            if "event" in keys:
                event = data['event']
                if event == "new":
                    order = data['order']
                    orderText = f"""
                    New Order -> {order['id']}, {order['type']}, {order['side']}.
                    Status: {order['status']}
                    """
                    print(f"\n{Fore.LIGHTYELLOW_EX}{inspect.cleandoc(orderText)}")
                # if event == "pending_new":
                    # print(data['order'])

        if self.type == "data":
            if "ev" in keys and data['ev'] == "AM":
                volume: int = data['v']
                accumulatedVolume: int = data['av']
                officialOpen: float = data['op']
                vwap: float = data['vw']
                open: float = data['o']
                high: float = data['h']
                low: float = data['l']
                close: float = data['c']
                average: float = data['a']
                # Divide data['s'] by 1000 to convert milliseconds to seconds
                timeStart = DM.convertTime(data['s'] / 1000)
                timeEnd = DM.convertTime(data['e'] / 1000)

                print(f"{Fore.LIGHTYELLOW_EX}[{timeStart}] -> New {data['T']} minute data.")
                self.sqlManager.checkTable(self.symbol)
                # Attempt to add data to table
                try:
                    self.sqlManager.addData(self.symbol, timeStart, open, high, low, close, volume)
                except Exception as error:
                    print(f"ERROR ADDING DATA! -> {str(error)}")
                # Calculate current hour data
                try:
                    self.dataManager.calculateCurrentHour()
                except Exception as error:
                    print(f"ERROR CALCULATING CURRENT HOUR! -> {str(error)}")
                # Update hourly table with indicators
                try:
                    self.dataManager.calculateHourlyIndicators()
                except Exception as error:
                    print(f"ERROR CALCULATING HOURLY INDICATORS! -> {str(error)}")

                # Don't analyze every minute update otherwise might get marked as PDT.
                # self.dataManager.analyzeIndicators()