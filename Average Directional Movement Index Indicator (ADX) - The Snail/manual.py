import pandas as pd
import pandas_ta as ta

data = pd.read_csv(f'./Datasets/BTCUSDT-1m-2023-05-22.csv') # 1
# data = pd.read_csv(f'./Datasets/BTCUSDT-3m-2023-05-22.csv') # 2
# data = pd.read_csv(f'./Datasets/BTCUSDT-5m-2023-05-22.csv') # 3
# data = pd.read_csv(f'./Datasets/BTCUSDT-4h-2018-2022.csv') # 4

data['Timestamp'] = pd.to_datetime(data['Timestamp'], unit='ms')
data.set_index('Timestamp', inplace=True) # Set datetime as index column

dillen = 14

def tr(df):
    # max(high - low, abs(high - close[1]), abs(low - close[1]))
    new_serie = [None]

    for i in range(1, len(df)):
        high = df['High'][i]
        low = df['Low'][i]
        close_1 = df['Close'][i-1]

        val = max(high-low, abs(high - close_1), abs(low-close_1))
        new_serie.append(val)
    
    return pd.Series(new_serie)

def change(serie):
    new_serie = [None]

    for i in range(0, len(serie)-1):
        new_serie.append(serie[i+1] - serie[i])

    return pd.Series(new_serie)

def dirmov(len):
    up = change(data['High'])
    down = change(data['Low'])

    _tr = tr(df=data)
    truerange = ta.rma(_tr, len)

    plus_serie = [None]
    for i in range(1, up.__len__()):
        if(up[i] > down[i] and up[i] > 0):
            plus_serie.append(up[i])
        else:
            plus_serie.append(0)

    plus_serie = pd.Series(plus_serie)
    plus_serie_rma = ta.rma(plus_serie)

    plus = []
    for i in range(plus_serie_rma.__len__()):
        plus.append(100 * plus_serie_rma[i] / truerange[i])

    plus = pd.Series(plus)

    minus_serie = [None]
    for i in range(1, up.__len__()):
        if(down[i] > up[i] and down[i] > 0):
            minus_serie.append(up[i])
        else:
            minus_serie.append(0)

    minus_serie = pd.Series(minus_serie)
    minus_serie_rma = ta.rma(minus_serie)
    
    minus = []
    for i in range(minus_serie_rma.__len__()):
        minus.append(100 * minus_serie_rma[i] / truerange[i])

    minus = pd.Series(minus)
    
    return plus, minus

def adx(dillen):
    plus, minus = dirmov(dillen)

    sum = []
    for i in range(len(plus)):
        if plus[i] != None or minus[i] != None:
            sum.append(plus[i] + minus[i])
        else:
            sum.append(None)

    sum = pd.Series(sum)

    _temp = []
    for i in range(len(sum)):
        if(sum[i] != None):
            if(sum[i] == 0):
                _temp.append(abs(plus[i] - minus[i]))
            else:
                _temp.append(abs(plus[i] - minus[i]) / sum[i])
        else:
            _temp.append(None)

    _temp = ta.rma(pd.Series(_temp))

    adx = []
    for i in range(len(_temp)):
        if(_temp[i] != None):
            adx.append(_temp[i] * 100)
        else:
            adx.append(_temp[i])

    adx = pd.Series(adx)
    return adx, plus, minus


print(adx(dillen))