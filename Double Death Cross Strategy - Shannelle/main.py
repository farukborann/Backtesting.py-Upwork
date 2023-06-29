from backtesting import Backtest, Strategy
from backtesting.lib import crossover
import pandas as pd
import talib as ta

MAX_DISTANCE = 40 # Maximum distance between two cross (50x100 and 50x200)

class Double_Death_Cross(Strategy):
    def init(self):
        close_series = self.data.Close.to_series()

        self.sma_50 = self.I(ta.SMA, close_series, 50)
        self.sma_100 = self.I(ta.SMA, close_series, 100)
        self.sma_200 = self.I(ta.SMA, close_series, 200)

        self.Distance_50x200 = 0
        self.Distance_50x100 = 0

    def next(self):
        if not crossover(self.sma_50, self.sma_200): 
            self.Distance_50x200 = self.Distance_50x200 + 1
        else:
            self.Distance_50x200 = 0

        if not crossover(self.sma_50, self.sma_100):
            self.Distance_50x100 = self.Distance_50x100 + 1
        else:
            self.Distance_50x100 = 0
        
        if (self.Distance_50x100 == 0 and self.Distance_50x200 < MAX_DISTANCE) or (self.Distance_50x200 == 0 and self.Distance_50x100 < MAX_DISTANCE):
            self.buy(size=-1, tp=self.data.Close[-1] * 0.90, sl=self.data.Close[-1] * 1.07)
            
        return

# data = pd.read_csv(f'./Datasets/BTCUSDT-1m-2023-05-22.csv') # 1
# data = pd.read_csv(f'./Datasets/BTCUSDT-3m-2023-05-22.csv') # 2
# data = pd.read_csv(f'./Datasets/BTCUSDT-5m-2023-05-22.csv') # 3
data = pd.read_csv(f'./Datasets/BTCUSDT-4h-2018-2022.csv') # 4

data['Timestamp'] = pd.to_datetime(data['Timestamp'], unit='ms')
data.set_index('Timestamp', inplace=True) # Set datetime as index column

backtest = Backtest(data, Double_Death_Cross, cash=100_000, exclusive_orders=True)
result=backtest.run()

res_file = open('result.txt', 'w')
res_file.write(str(result))
res_file.close()

backtest.plot()
