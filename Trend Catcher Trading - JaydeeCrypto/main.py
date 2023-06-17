from backtesting import Backtest, Strategy
from backtesting.test import GOOG
from backtesting.lib import crossover
import pandas as pd
import talib as ta

class Trend_Catcher_Trading(Strategy):
    def init(self):
        close_series = self.data.Close.to_series()

        self.ema_5 = self.I(ta.SMA, close_series, 5)
        self.ema_10 = self.I(ta.SMA, close_series, 10)
        self.ema_20 = self.I(ta.SMA, close_series, 20)
        self.rsi = self.I(ta.RSI, close_series, 14)

    def next(self):
        if crossover(self.ema_10, self.ema_5) and crossover(self.ema_20, self.ema_10):
            if self.rsi[-1] >= 50:
                self.buy(size=1 ,sl=self.data.Close[-1] * 0.99, tp=self.data.Close[-1] * 1.02) # Buy Order

data = pd.read_csv(f'./Datasets/BTCUSDT-1m-2023-05-22.csv') # 1
# data = pd.read_csv(f'./Datasets/BTCUSDT-3m-2023-05-22.csv') # 2
# data = pd.read_csv(f'./Datasets/BTCUSDT-5m-2023-05-22.csv') # 3
# data = pd.read_csv(f'./Datasets/BTCUSDT-4h-2018-2022.csv') # 4
# data = pd.read_csv(f'./Datasets/06.06 - 06.11 2023 BTCUSDT 1h.csv') # 4

data['Timestamp'] = pd.to_datetime(data['Timestamp'], unit='ms')
data.set_index('Timestamp', inplace=True) # Set datetime as index column

backtest = Backtest(data, Trend_Catcher_Trading, exclusive_orders=True, cash=100_000) # exclusive_orders => each new order auto-closes the previous trade/position
result=backtest.run()

res_file = open('result.txt', 'w')
res_file.write(str(result))
res_file.close()

backtest.plot()
