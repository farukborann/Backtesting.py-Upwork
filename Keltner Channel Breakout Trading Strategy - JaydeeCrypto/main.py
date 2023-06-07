from backtesting import Backtest, Strategy
from backtesting.test import GOOG
import pandas as pd

def KC(high, low, close, kc_length=20, multiplier=2, atr_length=10):
    tr1 = pd.DataFrame(high - low)
    tr2 = pd.DataFrame(abs(high - close.shift()))
    tr3 = pd.DataFrame(abs(low - close.shift()))
    frames = [tr1, tr2, tr3]
    tr = pd.concat(frames, axis = 1, join = 'inner').max(axis = 1)
    atr = tr.ewm(alpha = 1/atr_length).mean()
    
    middle = close.ewm(kc_length).mean()
    upper = close.ewm(kc_length).mean() + multiplier * atr
    lower = close.ewm(kc_length).mean() - multiplier * atr
    
    return upper, middle, lower

class KernelChannel(Strategy):
    def init(self):
        high_series = self.data.High.to_series()
        low_series = self.data.Low.to_series()
        close_series = self.data.Close.to_series()

        self.kc = self.I(KC, high_series, low_series, close_series, name='KC')

        self.orderType = None

    def next(self):
        if self.data.Close[-1] > self.kc[0][-1] and not self.position.is_short: # Short Order if its not on short position
            self.buy(size=-1, sl=self.data.Close[-1] * 1.01, tp=self.data.Close[-1] * 0.99)
        elif self.data.Close[-1] < self.kc[2][-1] and not self.position.is_long: # Long Order if its not on short position
            self.buy(size=1, sl=self.data.Close[-1] * 0.99, tp=self.data.Close[-1] * 1.01)

data = pd.read_csv(f'./Datasets/BTCUSDT-1m-2023-05-22.csv') # 1
# data = pd.read_csv(f'./Datasets/BTCUSDT-3m-2023-05-22.csv') # 2
# data = pd.read_csv(f'./Datasets/BTCUSDT-5m-2023-05-22.csv') # 3
# data = pd.read_csv(f'./Datasets/BTCUSDT-4h-2018-2022.csv') # 4

data['Timestamp'] = pd.to_datetime(data['Timestamp'], unit='ms')
data.set_index('Timestamp', inplace=True) # Set datetime as index column

backtest = Backtest(data, KernelChannel, exclusive_orders=True, cash=100_000) # exclusive_orders => each new order auto-closes the previous trade/position
result=backtest.run()

res_file = open('result.txt', 'w')
res_file.write(str(result))
res_file.close()

backtest.plot()
