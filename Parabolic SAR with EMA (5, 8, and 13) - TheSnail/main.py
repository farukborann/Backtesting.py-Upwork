from backtesting import Backtest, Strategy
from backtesting.test import GOOG
from backtesting.lib import crossover
import pandas as pd
import talib as ta

class PSAR_EMA(Strategy):
    def init(self):
        high_series = self.data.High.to_series()
        low_series = self.data.Low.to_series()
        close_series = self.data.Close.to_series()

        self.ema_5 = self.I(ta.EMA, close_series, 5)
        self.ema_8 = self.I(ta.EMA, close_series, 8)
        self.ema_13 = self.I(ta.EMA, close_series, 13)
        self.sar = self.I(ta.SAR, high_series, low_series, scatter=True)

    def next(self):
        if crossover(self.ema_8, self.ema_5) and crossover(self.ema_13, self.ema_5) and crossover(self.ema_13, self.ema_8):
            if self.sar[-1] > self.sar[-2]: # SAR indicating an uptrend.
                self.buy(size=1 ,sl=self.data.Close[-1] * 0.99, tp=self.data.Close[-1] * 1.02) # Long Order
        if crossover(self.ema_5, self.ema_8) and crossover(self.ema_5, self.ema_13) and crossover(self.ema_8, self.ema_13):
            if self.sar[-1] < self.sar[-2]: # SAR indicating an downtrend.
                self.buy(size=-1, sl=self.data.Close[-1] * 1.02, tp=self.data.Close[-1] * 0.99) # Short order

data = pd.read_csv(f'./Datasets/BTCUSDT-1m-2023-05-22.csv') # 1
# data = pd.read_csv(f'./Datasets/BTCUSDT-3m-2023-05-22.csv') # 2
# data = pd.read_csv(f'./Datasets/BTCUSDT-5m-2023-05-22.csv') # 3
# data = pd.read_csv(f'./Datasets/BTCUSDT-4h-2018-2022.csv') # 4

data['Timestamp'] = pd.to_datetime(data['Timestamp'], unit='ms')
data.set_index('Timestamp', inplace=True) # Set datetime as index column

backtest = Backtest(data, PSAR_EMA, exclusive_orders=True, cash=100_000) # exclusive_orders => each new order auto-closes the previous trade/position
result=backtest.run()

res_file = open('result.txt', 'w')
res_file.write(str(result))
res_file.close()

backtest.plot()
