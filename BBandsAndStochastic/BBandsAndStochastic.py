from backtesting import Backtest, Strategy
from backtesting.lib import crossover
from backtesting.test import GOOG # Test data
import pandas as pd
import talib as ta

Oversold = 1
Overbought = 2

HitLowerBand = 1
HitUpperBand = 2

def StochasticStatus(stochastic):
    if stochastic[0][-1] < 20 and stochastic[1][-1] < 20:
        return Oversold
    elif stochastic[0][-1] > 80 and stochastic[1][-1] > 80:
        return Overbought
    
    return None
    
def BollingerStatus(bollinger, high, low):
    if low[-1] <= bollinger[2][-1]:
        return HitLowerBand
    elif high[-1] >= bollinger[0][-1]:
        return HitUpperBand
    
    return None

class BBandsAndStochastic(Strategy):
    def init(self):
        high_series = self.data.High.to_series()
        low_series = self.data.Low.to_series()
        close_series = self.data.Close.to_series()

        self.bbands = self.I(ta.BBANDS, close_series, name='Bollinger Bands') # Upper => 0, Middle => 1, Lower => 2
        self.stochastic = self.I(ta.STOCH, high_series, low_series, close_series, name='Stochastic')

    def next(self):
        BBandsStatus = BollingerStatus(self.bbands, self.data.High, self.data.Low)

        if self.position:
            if (self.position.is_long and BBandsStatus == HitUpperBand) or (self.position.is_short and BBandsStatus == HitLowerBand):
                self.position.close()
        
        else:
            StochStatus = StochasticStatus(self.stochastic)

            if BBandsStatus == HitLowerBand and StochStatus == Oversold:
                self.buy(size=1) # Long
            elif BBandsStatus == HitUpperBand and StochStatus == Overbought:
                self.buy(size=-1) # Short
                return

data = pd.read_csv(f'./Datasets/BTCUSDT-1m-2023-05-22.csv') # 1
# data = pd.read_csv(f'./Datasets/BTCUSDT-3m-2023-05-22.csv') # 2
# data = pd.read_csv(f'./Datasets/BTCUSDT-5m-2023-05-22.csv') # 3
# data = pd.read_csv(f'./Datasets/BTCUSDT-4h-2018-2022.csv', sep=',') # 4

data['Timestamp'] = pd.to_datetime(data['Timestamp'], unit='ms')
data.set_index('Timestamp', inplace=True) # Set datetime as index column
# data['Volume'] = data['Volume'] * 1e2 # Fix volume column

backtest = Backtest(data, BBandsAndStochastic, cash=100_000)
result=backtest.run()

res_file = open('result.txt', 'w')
res_file.write(str(result))
res_file.close()

backtest.plot()
