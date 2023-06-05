from backtesting import Backtest, Strategy
from backtesting.lib import crossover
import pandas as pd
import talib as ta

class Golden_Cross(Strategy):
    def init(self):
        close_series = self.data.Close.to_series()

        self.sma_50 = self.I(ta.SMA, close_series, 50)
        self.sma_200 = self.I(ta.SMA, close_series, 200)

    def next(self):
        if(crossover(self.sma_200, self.sma_50) and self.position):
            self.buy(size=-1)
        elif(crossover(self.sma_50, self.sma_200)):
            self.buy(size=1)
            
        return


# data = pd.read_csv(f'./Datasets/BTCUSDT-1m-2023-05-22.csv') # 1
# data = pd.read_csv(f'./Datasets/BTCUSDT-3m-2023-05-22.csv') # 2
# data = pd.read_csv(f'./Datasets/BTCUSDT-5m-2023-05-22.csv') # 3
data = pd.read_csv(f'./Datasets/BTCUSDT-4h-2018-2022.csv') # 4

data['Timestamp'] = pd.to_datetime(data['Timestamp'], unit='ms')
data.set_index('Timestamp', inplace=True) # Set datetime as index column

backtest = Backtest(data, Golden_Cross)
result=backtest.run()

res_file = open('result.txt', 'w')
res_file.write(str(result))
res_file.close()

backtest.plot()
