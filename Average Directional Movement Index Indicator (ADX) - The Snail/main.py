from backtesting import Backtest, Strategy
from backtesting.test import GOOG
from backtesting.lib import crossover
import pandas as pd
import pandas_ta as ta

class MACD_SAR_EMA(Strategy):
    def init(self):
        high_series = self.data.High.to_series()
        low_series = self.data.Low.to_series()
        close_series = self.data.Close.to_series()

        # self.adx => [adx, positive, negative]
        self.adx = self.I(ta.adx, high_series, low_series, close_series)

    def next(self):
        if crossover(self.adx[1], self.adx[2]):
            self.buy(size=1)
        elif crossover(self.adx[2], self.adx[1]):
            self.buy(size=-1)
        pass

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
