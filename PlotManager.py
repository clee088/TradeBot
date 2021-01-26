import pandas as pd
import mplfinance as mpf
import numpy as np

class PlotManager():

    def __init__(self, symbol, sqlhoursManager):
        self.symbol = symbol
        self.sqlHoursManager = sqlhoursManager

    def calculateBuyMACDSignals(self):
        signals = []
        df = self.sqlHoursManager.createDF(self.symbol)
        df['time'] = pd.to_datetime(df['time'])
        df.set_index('time', inplace=True)
        previous = df['macdHistogram'][-1]
        for date,macd in df['macdHistogram'].iteritems():
            if previous <= 0 and macd > previous and macd > 0:
                signals.append(-0.5)
            else:
                signals.append(np.nan)
            previous = macd
        return signals

    def calculateSellMACDSignals(self):
        signals = []
        df = self.sqlHoursManager.createDF(self.symbol)
        df['time'] = pd.to_datetime(df['time'])
        df.set_index('time', inplace=True)
        previous = df['macdHistogram'][-1]
        for date,macd in df['macdHistogram'].iteritems():
            if previous >= 0 and macd < previous and macd < 0:
                signals.append(0.5)
            else:
                signals.append(np.nan)
            previous = macd
        return signals

    def plotHourlyChart(self):
        # DataFrame setup
        df = self.sqlHoursManager.createDF(self.symbol)
        df['time'] = pd.to_datetime(df['time'])
        df.set_index('time', inplace=True)
        df.rename(columns={"time": "Date"}, inplace=True)

        # Indicators
        hmas = df[['hmaFast', 'hmaSlow']]
        macdHistogram = df[['macdHistogram']]
        slope = df[['slope']]
        macdBuySignal = self.calculateBuyMACDSignals()
        macdSellSignal = self.calculateSellMACDSignals()
        hmaPlot = mpf.make_addplot(hmas, width=1)
        macdPlot = mpf.make_addplot(macdHistogram, panel=2, type='bar',secondary_y=False, ylabel="MACD \nHistogram")
        slopePlot = mpf.make_addplot(slope, panel=3, type='line', secondary_y=False, ylabel="HMA 34 Slope", color="orange")
        signalsMACDBuyPlot = mpf.make_addplot(macdBuySignal, panel=2, type='scatter', secondary_y=False, markersize=100,
                                              marker='^', color="g")
        signalsMACDSellPlot = mpf.make_addplot(macdSellSignal, panel=2, type='scatter', secondary_y=False, markersize=100,
                                              marker='v', color="r")

        plots = [hmaPlot, macdPlot, slopePlot, signalsMACDBuyPlot, signalsMACDSellPlot]

        mpf.plot(df, title=f"{self.symbol} Hourly Price", type='candle', style='yahoo', volume=True, addplot=plots, block=False)
        mpf.show()