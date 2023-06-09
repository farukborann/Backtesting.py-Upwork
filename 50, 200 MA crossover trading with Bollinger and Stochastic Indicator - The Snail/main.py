from backtesting import Backtest, Strategy
from backtesting.lib import crossover
from backtesting.test import GOOG # Test data
import pandas as pd
import talib as ta

OVERSOLD = 1
OVERBOUGHT = 2

BB_LOWER = 1
BB_UPPER = 2

EMA_CROSS_ABOVE = 1
EMA_CROSS_BELOW = 2

def StochasticStatus(stochastic):
    if stochastic[0][-1] < 20 or stochastic[1][-1] < 20:
        return OVERSOLD
    elif stochastic[0][-1] > 80 or stochastic[1][-1] > 80:
        return OVERBOUGHT
    
    return None
    
def BollingerStatus(bollinger, high, low):
    if low[-1] <= bollinger[2][-1]:
        return BB_LOWER
    elif high[-1] >= bollinger[0][-1]:
        return EMA_CROSS_BELOW
    
    return None

def EMAsStatus(ema_50, ema_200):
    if crossover(ema_50, ema_200):
        return EMA_CROSS_ABOVE
    elif crossover(ema_200, ema_50):
        return EMA_CROSS_BELOW
    else:
        return None

class EMAsAndBBandsAndStochastic(Strategy):
    def init(self):
        high_series = self.data.High.to_series()
        low_series = self.data.Low.to_series()
        close_series = self.data.Close.to_series()

        self.ema_50 = self.I(ta.EMA, close_series, 50)
        self.ema_200 = self.I(ta.EMA, close_series, 200)
        self.bbands = self.I(ta.BBANDS, close_series, name='Bollinger Bands') # Upper => 0, Middle => 1, Lower => 2
        self.stochastic = self.I(ta.STOCH, high_series, low_series, close_series, name='Stochastic')

        self.LastEmaCross = None

    def next(self):
        # if emas crossing update the last cross
        EMAStatus = EMAsStatus(self.ema_50, self.ema_200)
        if EMAStatus != None:
            self.LastEmaCross = EMAStatus

        BBandsStatus = BollingerStatus(self.bbands, self.data.High, self.data.Low)
        StochStatus = StochasticStatus(self.stochastic)

        if not self.position: # if its not on position
            # if last ema cross is above and low price cross down bb and stockhastic is oversold
            if self.LastEmaCross == EMA_CROSS_ABOVE and BBandsStatus == BB_LOWER and StochStatus == OVERSOLD:
                self.buy(size=1) # long order       sl=self.data.Close[-1]*0.98, tp=self.data.Close[-1]*1.02
                self.LastEmaCross = None
            # if last ema cross is below and high price cross up bb and stockhastic is overbought
            elif self.LastEmaCross == EMA_CROSS_BELOW and BBandsStatus == BB_UPPER and StochStatus == OVERBOUGHT:
                self.buy(size=-1) # short order     sl=self.data.Close[-1]*1.02, tp=self.data.Close[-1]*0.98
                self.LastEmaCross = None
        else: # if its on position
            if self.position.is_long and (self.LastEmaCross == EMA_CROSS_BELOW or BBandsStatus == BB_UPPER):
                self.position.close()
            elif self.position.is_short and (self.LastEmaCross == EMA_CROSS_ABOVE or BBandsStatus == BB_LOWER):
                self.position.close()

# data = pd.read_csv(f'./Datasets/BTCUSDT-1m-2023-05-22.csv') # 1
# data = pd.read_csv(f'./Datasets/BTCUSDT-3m-2023-05-22.csv') # 2
# data = pd.read_csv(f'./Datasets/BTCUSDT-5m-2023-05-22.csv') # 3
data = pd.read_csv(f'./Datasets/BTCUSDT-4h-2018-2022.csv', sep=',') # 4

data['Timestamp'] = pd.to_datetime(data['Timestamp'], unit='ms')
data.set_index('Timestamp', inplace=True) # Set datetime as index column

backtest = Backtest(data, EMAsAndBBandsAndStochastic, cash=100_000)
result=backtest.run()

res_file = open('result.txt', 'w')
res_file.write(str(result))
res_file.close()

backtest.plot()
