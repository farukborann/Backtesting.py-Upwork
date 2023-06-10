from backtesting import Backtest, Strategy
from backtesting.lib import crossover
import pandas as pd
import pandas_ta
import numpy as np

OBV_SHORT = 1
OBV_LONG = 2

def OBV_With_SMA(close_series, volume_series):
    obv = pandas_ta.obv(close_series, volume_series)
    sma = pandas_ta.sma(obv)

    return obv, sma

def OBV_Status(obv_with_sma):
    obv = obv_with_sma[0]
    sma = obv_with_sma[1]

    if crossover(sma, obv): # Short
        return OBV_SHORT
    elif crossover(obv, sma):
        return OBV_LONG

    return None

def OverLevels(indicator_values):
    overbougth = []
    oversold = []

    for val in indicator_values:
        overbougth.append(80)
        oversold.append(20)

    return indicator_values, np.array(overbougth), np.array(oversold)


class Herding_Indicators_Trading_Strategy(Strategy):
    def init(self):
        high_series = self.data.High.to_series()
        low_series = self.data.Low.to_series()
        close_series = self.data.Close.to_series()
        volume_series = self.data.Volume.to_series()

        self.obv_with_sma = self.I(OBV_With_SMA, close_series, volume_series)
        self.mfi = self.I(OverLevels, pandas_ta.mfi(high_series, low_series, close_series, volume_series))
        self.rsi = self.I(OverLevels, pandas_ta.rsi(close_series))

    def next(self):
        OBVStatus = OBV_Status(self.obv_with_sma)

        if OBVStatus == OBV_LONG and (self.mfi[0][-1] < 20 or self.rsi[0][-1] < 20):
            self.buy(size=1, tp=self.data.Close[-1] * 1.02, sl=self.data.Close[-1] * 0.099)
        elif OBVStatus == OBV_SHORT and (self.mfi[0][-1] > 80 or self.rsi[0][-1] > 80):
            self.buy(size=-1, tp=self.data.Close[-1] * 0.98, sl=self.data.Close[-1] * 1.001)

data = pd.read_csv(f'./Datasets/BTCUSDT-1m-2023-05-22.csv') # 1
# data = pd.read_csv(f'./Datasets/BTCUSDT-3m-2023-05-22.csv') # 2
# data = pd.read_csv(f'./Datasets/BTCUSDT-5m-2023-05-22.csv') # 3
# data = pd.read_csv(f'./Datasets/BTCUSDT-4h-2018-2022.csv') # 4

data['Timestamp'] = pd.to_datetime(data['Timestamp'], unit='ms')
data.set_index('Timestamp', inplace=True) # Set datetime as index column

backtest = Backtest(data, Herding_Indicators_Trading_Strategy, exclusive_orders=True, cash=100_000)
result=backtest.run()

res_file = open('result.txt', 'w')
res_file.write(str(result))
res_file.close()

backtest.plot()