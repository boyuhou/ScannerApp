import collections
import numpy as np
import pandas as pd

def numpy_ewma_vectorized(data, window):

    alpha = 2 /(window + 1.0)
    alpha_rev = 1-alpha

    scale = 1/alpha_rev
    n = data.shape[0]

    r = np.arange(n)
    scale_arr = scale**r
    offset = data[0]*alpha_rev**(r+1)
    pw0 = alpha*alpha_rev**(n-1)

    mult = data*pw0*scale_arr
    cumsums = mult.cumsum()
    out = offset + cumsums*scale_arr[::-1]
    return out[-1]


class Ticker:
    def __init__(self, ticker):
        self.ticker = ticker
        self.price_dict = {
            1: pd.DataFrame(columns=['open', 'high', 'low', 'close']),
            5: pd.DataFrame(columns=['open', 'high', 'low','close']),
            15: pd.DataFrame(columns=['open', 'high', 'low', 'close']),
            60: pd.DataFrame(columns=['open', 'high', 'low', 'close']),
            240: pd.DataFrame(columns=['open', 'high', 'low', 'close']),
        }
        self.indicator_dict = {
            1: pd.DataFrame(columns=['ema8', 'ema21', 'ema50', 'adx14', 'range20', 'tsi']),
            5: pd.DataFrame(columns=['ema8', 'ema21', 'ema50', 'adx14', 'range20', 'tsi']),
            15: pd.DataFrame(columns=['ema8', 'ema21', 'ema50', 'adx14', 'range20', 'tsi']),
            60: pd.DataFrame(columns=['ema8', 'ema21', 'ema50', 'adx14', 'range20', 'tsi']),
            240: pd.DataFrame(columns=['ema8', 'ema21', 'ema50', 'adx14', 'range20', 'tsi']),
        }

    def insert_new_price(self, time_interval, open, high, low, close, quote_time):
        new_df = pd.DataFrame({
            'open': open,
            'high': high,
            'low': low,
            'close': close,
        }, index=[pd.to_datetime(quote_time)])
        self.price_dict[time_interval] = self.price_dict[time_interval].append(new_df)

    def update_indicator(self, interval):
        multiplier = 100.0 if 'JPY' in self.ticker else 10000.0
        df = self.price_dict[interval][['close']]
        df.loc[:, 'ema8'] = df['close'].ewm(span=8).mean()
        df.loc[:, 'ema21'] = df['close'].ewm(span=21).mean()
        df.loc[:, 'ema50'] = df['close'].ewm(span=50).mean()
        df.loc[:, 'range20'] = (df['close'].rolling(window=20).max() - df['close'].rolling(
            window=20).min()) * multiplier

        percentage_change = (df['close'] - df['close'].shift(1)) / df['close'].shift(1)
        df.loc[:, 'tsi'] = percentage_change.rolling(window=200).mean() / percentage_change.rolling(
            window=200).std() * 10
        df['adx14'] = _average_directional_movement_index(df, 14)
        self.indicator_dict[interval] = df['ema8', 'ema21', 'ema50', 'adx14', 'range20', 'tsi']


def _get_adx_sum(s, n):
    result = s.tolist()
    initial_sum = sum(s[n:(n - 1) * 2 + 1])
    result[(n - 1) * 2 + 1] = initial_sum
    for i in range(n * 2, len(s.index)):
        result[i] = (result[i - 1] * 13 + result[i]) / n
    return pd.Series(data=result, index=s.index)


def _get_ema_value(s, n):
    initial_sum_value = s.rolling(window=n, min_periods=n).sum().iloc[n]
    result = s.tolist()
    result[n] = initial_sum_value
    for i in range(n + 1, len(s.index)):
        result[i] = result[i - 1] - (result[i - 1] / n) + result[i]
    return pd.Series(data=result, index=s.index)


def _average_directional_movement_index(df, n):
    adx = df[['high', 'close', 'low']]
    adx.loc[:, 'tr'] = pd.concat([(df['high'] - df['low']), (df['high'] - df['close'].shift(1)).abs(),
                                  (df['close'] - df['close'].shift(1)).abs()], axis=1).max(axis=1)
    adx.loc[:, 'dmplus'] = 0
    adx.loc[:, 'dmdown'] = 0
    adx.loc[:, 'high_diff'] = df['high'] - df['high'].shift(1)
    adx.loc[:, 'low_diff'] = df['low'].shift(1) - df['low']
    adx.loc[((adx['high_diff'] > adx['low_diff']) & (adx['high_diff'] > 0)), 'dmplus'] = adx['high_diff']
    adx.loc[((adx['high_diff'] < adx['low_diff']) & (adx['low_diff'] > 0)), 'dmdown'] = adx['low_diff']
    adx['tr' + str(n)] = _get_ema_value(adx['tr'], n)
    adx['dmplus' + str(n)] = _get_ema_value(adx['dmplus'], n)
    adx['dmdown' + str(n)] = _get_ema_value(adx['dmdown'], n)
    adx['diplus' + str(n)] = 100 * adx['dmplus' + str(n)] / adx['tr' + str(n)]
    adx['didown' + str(n)] = 100 * adx['dmdown' + str(n)] / adx['tr' + str(n)]
    adx['didiff' + str(n)] = (adx['diplus' + str(n)] - adx['didown' + str(n)]).abs()
    adx['disum' + str(n)] = (adx['diplus' + str(n)] + adx['didown' + str(n)])
    adx['dx' + str(n)] = 100 * adx['didiff' + str(n)] / adx['disum' + str(n)]
    adx['adx' + str(n)] = _get_adx_sum(adx['dx' + str(n)], n)
    return adx['adx' + str(n)]