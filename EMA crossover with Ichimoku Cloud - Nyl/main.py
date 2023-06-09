from backtesting import Backtest, Strategy
from backtesting.lib import crossover
from backtesting.test import GOOG
import pandas as pd
import talib as ta

def ichimoku_tenkan(high, low, periot=9):
    if(len(high) != len(low)):
        raise Exception('Not valid collections')

    # TenkanSen Calculation #
    tenkan_values = []
    # Fill incalculable indexs with None
    for i in range(periot-1):
        tenkan_values.append(None)

    # Find highest and lowest values from last 9 (tenkan_periot) periot
    for tick in range(periot, len(high)+1):
        hp = high[tick-periot: tick]
        lp = low[tick-periot: tick]

        # Find max value in high values and min value from low values
        h_max = max(hp)
        l_min = min(lp)

        # Calculate Tenkan Value
        tenkan = (h_max + l_min) / 2

        # Append the results array
        tenkan_values.append(tenkan)

    # Convert arrays to pandas series and return
    return pd.Series(tenkan_values)

def ichimoku_kijun(high, low, periot=26):
    if(len(high) != len(low)):
        raise Exception('Not valid collections')
    
    # Same with Tenkan but with 26 (periot) periot
    kijun_values = []
    for i in range(periot-1):
        kijun_values.append(None)
    kijun_range = range(periot, len(high)+1)

    for tick in kijun_range:
        hp = high[tick-periot: tick]
        lp = low[tick-periot: tick]

        h_max = max(hp)
        l_min = min(lp)

        kijun = (h_max + l_min) / 2

        kijun_values.append(kijun)

    # Convert arrays to pandas series and return
    return pd.Series(kijun_values)

class EMA_Ichimoku(Strategy):
    def init(self):
        high_series = self.data.High.to_series()
        low_series = self.data.Low.to_series()
        close_series = self.data.Close.to_series()

        self.ema_short = self.I(ta.EMA, close_series, 9)
        self.ema_long = self.I(ta.EMA, close_series, 26)

        self.ichimoku_tenkan = self.I(ichimoku_tenkan, high_series, low_series, name='Ichimoku Tenkan')
        self.ichimoku_kijun = self.I(ichimoku_kijun, high_series, low_series, name='Ichimoku Kijun')

    def next(self):
        max_ichimoku = max(self.ichimoku_tenkan[-1], self.ichimoku_kijun[-1])
        if(crossover(self.ema_short, self.ema_long) and self.data.Close[-1] > max_ichimoku):
            self.buy(size=1)
        elif(self.position and crossover(self.ema_long, self.ema_short)):
            self.position.close()
            # self.sell(size=-1)
            
        return


# data = pd.read_csv(f'./Datasets/BTCUSDT-1m-2023-05-22.csv') # 1
# data = pd.read_csv(f'./Datasets/BTCUSDT-3m-2023-05-22.csv') # 2
# data = pd.read_csv(f'./Datasets/BTCUSDT-5m-2023-05-22.csv') # 3
data = pd.read_csv(f'./Datasets/BTCUSDT-4h-2018-2022.csv') # 4

data['Timestamp'] = pd.to_datetime(data['Timestamp'], unit='ms')
data.set_index('Timestamp', inplace=True) # Set datetime as index column

backtest = Backtest(data, EMA_Ichimoku, trade_on_close=True, exclusive_orders=True, cash=100_000)
result=backtest.run()

res_file = open('result.txt', 'w')
res_file.write(str(result))
res_file.close()

backtest.plot()
