from backtesting import Backtest, Strategy
from backtesting.test import GOOG
import pandas as pd
import talib as ta

class MACD_SAR_EMA(Strategy):

    def init(self):
        high_series = self.data.High.to_series()
        low_series = self.data.Low.to_series()
        close_series = self.data.Close.to_series()

        self.ema_200 = self.I(ta.EMA, close_series, 200)
        self.macd = self.I(ta.MACD, close_series) # fast, slow, signal
        self.sar = self.I(ta.SAR, high_series, low_series, scatter=True)

    def next(self):
        if self.data.Close[-1] > self.ema_200[-1]: # current candle above the 200 EMA
            if self.sar[-1] > self.sar[-2]: # SAR indicating an uptrend.
                if self.macd[0][-1] > 0 and self.macd[0][-2] < 0: # Crossover of the histogram with 0
                    self.buy(size=1 ,sl=self.data.Close[-1] * 0.99, tp=self.data.Close[-1] * 1.02) # Long Order
        else: # current candle below 200 EMA
            if self.sar[-1] < self.sar[-2]: # SAR indicating an downtrend.
                if self.macd[0][-1] < 0 and self.macd[0][-2] > 0: # Crossunder of the histogram with 0
                    self.buy(size=-1, sl=self.data.Close[-1] * 1.02, tp=self.data.Close[-1] * 0.99) # Short order

data = pd.read_csv(f'./Datasets/BTCUSDT-1m-2023-05-22.csv') # 1
# data = pd.read_csv(f'./Datasets/BTCUSDT-3m-2023-05-22.csv') # 2
# data = pd.read_csv(f'./Datasets/BTCUSDT-5m-2023-05-22.csv') # 3
# data = pd.read_csv(f'./Datasets/BTCUSDT-4h-2018-2022.csv') # 4

data['Timestamp'] = pd.to_datetime(data['Timestamp'], unit='ms')
data.set_index('Timestamp', inplace=True) # Set datetime as index column

backtest = Backtest(data, MACD_SAR_EMA, exclusive_orders=True, cash=100_000) # exclusive_orders => each new order auto-closes the previous trade/position
result=backtest.run()

res_file = open('result.txt', 'w')
res_file.write(str(result))
res_file.close()

backtest.plot()
