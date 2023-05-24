from backtesting import Backtest, Strategy
from backtesting.lib import crossover
from backtesting.test import GOOG
import pandas as pd
import talib as ta

class EMAs_MACD_Stochastic_RSI(Strategy):

    def init(self):
        high_series = self.data.High.to_series()
        low_series = self.data.Low.to_series()
        close_series = self.data.Close.to_series()

        self.ema_5 = self.I(ta.EMA, close_series, 5)
        self.ema_15 = self.I(ta.EMA, close_series, 15)
        self.ema_50 = self.I(ta.EMA, close_series, 50)
        self.macd = self.I(ta.MACD, close_series, 12, 26, 9) # fast, slow, signal
        self.rsi = self.I(ta.RSI, close_series)
        self.stochastic = self.I(ta.STOCH, high_series, low_series, close_series)

    def next(self):
        macd = self.macd[0][-1]
        signal = self.macd[2][-1]

        is_stochastic_available = self.stochastic[0][-1] > 20 and crossover(self.stochastic[0], self.stochastic[1])
        is_ema_available = self.ema_5[-1] > self.ema_15[-1] and self.ema_5[-1] > self.ema_50[-1] and self.ema_15[-1] > self.ema_50[-1]
        is_macd_available = macd > signal
        is_rsi_avaialable = self.rsi[-1] < 30

        if(is_stochastic_available and is_ema_available and is_macd_available and is_rsi_avaialable):
            self.buy(sl=self.data.Close[-1] - 10)
        elif(self.position and self.rsi[-1] > 70):
            self.sell()
            
        return

    # def 

# data = pd.read_csv(f'./BTCUSDT-1m-2023-05-22.csv')
# data = pd.read_csv(f'./BTCUSDT-3m-2023-05-22.csv')
# data = pd.read_csv(f'./BTCUSDT-5m-2023-05-22.csv')
# data['Timestamp'] = pd.to_datetime(data['Timestamp'], unit='ms')

# data = pd.read_csv(f'./BTCUSDT-4h-2018-2022.csv')
# data['Timestamp'] = pd.to_datetime(data['Timestamp'], unit='s')

# data.set_index('Timestamp', inplace=True)
# print(data)

backtest = Backtest(GOOG, EMAs_MACD_Stochastic_RSI, trade_on_close=True, exclusive_orders=True)
result=backtest.run()

res_file = open('result.txt', 'w')
res_file.write(str(result))
res_file.close()

backtest.plot()
