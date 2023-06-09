from backtesting import Backtest, Strategy
from backtesting.test import GOOG
import pandas as pd
import pandas_ta as ta
import talib

def TC(high, low, close):
    pivot = ta.hlc3(high, low, close)
    bc = ta.hl2(high, low)
    
    tc = []
    for i in range(len(pivot)):
        pivot_i = pivot[i]
        bc_i = bc[i]

        if pivot_i == None or bc_i == None:
            tc.append(None)
        else:
            tc.append((pivot_i - bc_i) + pivot_i)

    return pd.Series(tc)

class CPR(Strategy):
    def init(self):
        high_series = self.data.High.to_series()
        low_series = self.data.Low.to_series()
        close_series = self.data.Close.to_series()

        self.difference = 10 # Minimum |bc - tc| for open order
        
        self.pivot = self.I(ta.hlc3, high_series, low_series, close_series, name='Pivot')
        self.bc = self.I(ta.hl2, high_series, low_series, name='BC')
        self.tc = self.I(TC, high_series, low_series, close_series, name='TC')
        self.sar = self.I(talib.SAR, high_series, low_series, scatter=True) # PSAR for trend

    def next(self):
        if abs(self.bc[-1] - self.tc[-1]) >= self.difference: # Check diffarence
            if self.sar[-1] > self.sar[-2]: # SAR indicating an uptrend.
               self.buy(size=1, sl=self.data.Low * 0.999) # Open long order
            elif self.sar[-1] < self.sar[-2]: # SAR indicating an downtrend.
               self.buy(size=-1, sl=self.data.High * 1.001) # Open short order
        elif self.position:
            if (self.position.is_long and self.sar[-1] < self.sar[-2]) or (self.position.is_short and self.sar[-1] > self.sar[-2]):
                self.position.close()


data = pd.read_csv(f'./Datasets/BTCUSDT-1m-2023-05-22.csv') # 1
# data = pd.read_csv(f'./Datasets/BTCUSDT-3m-2023-05-22.csv') # 2
# data = pd.read_csv(f'./Datasets/BTCUSDT-5m-2023-05-22.csv') # 3
# data = pd.read_csv(f'./Datasets/BTCUSDT-4h-2018-2022.csv') # 4

data['Timestamp'] = pd.to_datetime(data['Timestamp'], unit='ms')
data.set_index('Timestamp', inplace=True) # Set datetime as index column

backtest = Backtest(data, CPR, exclusive_orders=True, cash=100_000) # exclusive_orders => each new order auto-closes the previous trade/position
result=backtest.run()

res_file = open('result.txt', 'w')
res_file.write(str(result))
res_file.close()

backtest.plot()
