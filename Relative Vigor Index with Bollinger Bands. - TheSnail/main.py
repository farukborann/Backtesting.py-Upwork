from backtesting import Backtest, Strategy
from backtesting.test import GOOG
from backtesting.lib import crossover
import pandas as pd
import pandas_ta as ta

RVGI_OVERSOLD = -0.3
RVGI_OVERBOUGHT = 0.3

class Relative_Vigor_Index_with_Bollinger_Bands(Strategy):
    def init(self):
        open_series = self.data.Open.to_series()
        high_series = self.data.High.to_series()
        low_series = self.data.Low.to_series()
        close_series = self.data.Close.to_series()

        self.rvgi = self.I(ta.rvgi, open_series, high_series, low_series, close_series)
        self.bb = self.I(ta.bbands, close_series, overlay=True)

    def next(self):
        if self.bb[0][-1] > self.data.Low[-1] and self.rvgi[0][-1] < RVGI_OVERSOLD:
            self.buy(size=1 ,sl=self.data.Close[-1] * 0.99, tp=self.data.Close[-1] * 1.02) # Buy Order
        elif self.bb[2][-1] < self.data.High[-1] and self.rvgi[0][-1] > RVGI_OVERBOUGHT:
            self.buy(size=-1 ,sl=self.data.Close[-1] * 1.01, tp=self.data.Close[-1] * 0.98) # Sell Order

# data = pd.read_csv(f'./Datasets/BTCUSDT-1m-2023-05-22.csv') # 1
# data = pd.read_csv(f'./Datasets/BTCUSDT-3m-2023-05-22.csv') # 2
# data = pd.read_csv(f'./Datasets/BTCUSDT-5m-2023-05-22.csv') # 3
# data = pd.read_csv(f'./Datasets/BTCUSDT-4h-2018-2022.csv') # 4
data = pd.read_csv(f'./Datasets/06.06 - 06.11 2023 BTCUSDT 1h.csv') # 4

data['Timestamp'] = pd.to_datetime(data['Timestamp'], unit='ms')
data.set_index('Timestamp', inplace=True) # Set datetime as index column

backtest = Backtest(data, Relative_Vigor_Index_with_Bollinger_Bands, exclusive_orders=True, cash=100_000, trade_on_close=True) # exclusive_orders => each new order auto-closes the previous trade/position
result=backtest.run()

res_file = open('result.txt', 'w')
res_file.write(str(result))
res_file.close()

backtest.plot()
