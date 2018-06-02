import collections
import numpy as np
import pandas as pd


def numpy_ewma_vectorized(data, window):
    alpha = 2 / (window + 1.0)
    alpha_rev = 1 - alpha

    scale = 1 / alpha_rev
    n = data.shape[0]

    r = np.arange(n)
    scale_arr = scale ** r
    offset = data[0] * alpha_rev ** (r + 1)
    pw0 = alpha * alpha_rev ** (n - 1)

    mult = data * pw0 * scale_arr
    cumsums = mult.cumsum()
    out = offset + cumsums * scale_arr[::-1]
    return out[-1]

TSI_PERIOD = 200

class Ticker:
    def __init__(self, ticker):
        self.ticker = ticker
        self.close_price = {
            1: collections.deque(maxlen=TSI_PERIOD),
            5: collections.deque(maxlen=TSI_PERIOD),
            15: collections.deque(maxlen=TSI_PERIOD),
            60: collections.deque(maxlen=TSI_PERIOD),
            240: collections.deque(maxlen=TSI_PERIOD),
        }
        self.open_price = {
            1: collections.deque(maxlen=TSI_PERIOD),
            5: collections.deque(maxlen=TSI_PERIOD),
            15: collections.deque(maxlen=TSI_PERIOD),
            60: collections.deque(maxlen=TSI_PERIOD),
            240: collections.deque(maxlen=TSI_PERIOD),
        }
        self.high_price = {
            1: collections.deque(maxlen=TSI_PERIOD),
            5: collections.deque(maxlen=TSI_PERIOD),
            15: collections.deque(maxlen=TSI_PERIOD),
            60: collections.deque(maxlen=TSI_PERIOD),
            240: collections.deque(maxlen=TSI_PERIOD),
        }
        self.low_price = {
            1: collections.deque(maxlen=TSI_PERIOD),
            5: collections.deque(maxlen=TSI_PERIOD),
            15: collections.deque(maxlen=TSI_PERIOD),
            60: collections.deque(maxlen=TSI_PERIOD),
            240: collections.deque(maxlen=TSI_PERIOD),
        }
        self.quote_time = {
            1: collections.deque(maxlen=TSI_PERIOD),
            5: collections.deque(maxlen=TSI_PERIOD),
            15: collections.deque(maxlen=TSI_PERIOD),
            60: collections.deque(maxlen=TSI_PERIOD),
            240: collections.deque(maxlen=TSI_PERIOD),
        }
        self.ema = {
            8: {
                1: collections.deque(maxlen=TSI_PERIOD),
                5: collections.deque(maxlen=TSI_PERIOD),
                15: collections.deque(maxlen=TSI_PERIOD),
                60: collections.deque(maxlen=TSI_PERIOD),
                240: collections.deque(maxlen=TSI_PERIOD),
            },
            21: {
                1: collections.deque(maxlen=TSI_PERIOD),
                5: collections.deque(maxlen=TSI_PERIOD),
                15: collections.deque(maxlen=TSI_PERIOD),
                60: collections.deque(maxlen=TSI_PERIOD),
                240: collections.deque(maxlen=TSI_PERIOD),
            },
            50: {
                1: collections.deque(maxlen=TSI_PERIOD),
                5: collections.deque(maxlen=TSI_PERIOD),
                15: collections.deque(maxlen=TSI_PERIOD),
                60: collections.deque(maxlen=TSI_PERIOD),
                240: collections.deque(maxlen=TSI_PERIOD),
            }
        }
        self.price_change = {
            1: collections.deque(maxlen=TSI_PERIOD),
            5: collections.deque(maxlen=TSI_PERIOD),
            15: collections.deque(maxlen=TSI_PERIOD),
            60: collections.deque(maxlen=TSI_PERIOD),
            240: collections.deque(maxlen=TSI_PERIOD),
        }
        self.trend_smooth_indicator = {
            1: collections.deque(maxlen=TSI_PERIOD),
            5: collections.deque(maxlen=TSI_PERIOD),
            15: collections.deque(maxlen=TSI_PERIOD),
            60: collections.deque(maxlen=TSI_PERIOD),
            240: collections.deque(maxlen=TSI_PERIOD),
        }

        self.price_dict = {
            1: pd.DataFrame(columns=['open', 'high', 'low', 'close']),
            5: pd.DataFrame(columns=['open', 'high', 'low', 'close']),
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

    def insert_new_price(self, time_interval, open_p, high_p, low_p, close_p, quote_time):
        new_df = pd.DataFrame({
            'open': open_p,
            'high': high_p,
            'low': low_p,
            'close': close_p,
        }, index=[pd.to_datetime(quote_time)])
        self.price_dict[time_interval] = self.price_dict[time_interval].append(new_df)

        self.close_price[time_interval].append(close_p)
        self.open_price[time_interval].append(open_p)
        self.low_price[time_interval].append(low_p)
        self.high_price[time_interval].append(high_p)
        self.quote_time[time_interval].append(quote_time)

    def update_indicator(self, interval):
        multiplier = 100.0 if 'JPY' in self.ticker else 10000.0
        self._update_ema(interval, ema_window=8)
        self._update_ema(interval, ema_window=21)
        self._update_ema(interval, ema_window=50)

        self._update_price_change(interval)
        self._update_tsi(interval)

        if self.quote_time[interval][-1] >= '2018-06-01 16:40:00':
            print(self.quote_time[interval][-1] + '  EMA08:' + str(
                numpy_ewma_vectorized(np.asarray(self.close_price[interval]), 8)))
            print(self.quote_time[interval][-1] + '  EMA21' + str(
                numpy_ewma_vectorized(np.asarray(self.close_price[interval]), 21)))
            print(self.quote_time[interval][-1] + '  EMA50' + str(
                numpy_ewma_vectorized(np.asarray(self.close_price[interval]), 50)))

    def _update_price_change(self, interval):
        if len(self.close_price[interval]) < 2:
            self.price_change[interval].append(np.nan)
        else:
            self.price_change[interval].append((self.close_price[interval][-1] - self.close_price[interval][-2]) / self.close_price[interval][-2])

    def _update_tsi(self, interval):
        if len(self.price_change[interval]) < 200:
            self.trend_smooth_indicator[interval].append(np.nan)
        else:
            close_array = np.asarray(self.price_change[interval])
            mean = np.mean(close_array)
            std = np.std(close_array)
            self.trend_smooth_indicator[interval].append(mean / std * 10.)

    def _update_ema(self, interval, ema_window):
        if len(self.close_price[interval]) < ema_window:
            self.ema[ema_window][interval].append(
                numpy_ewma_vectorized(np.asarray(self.close_price[interval]), ema_window))
        else:
            self.ema[ema_window][interval].append(
                2. / (ema_window + 1) * (self.close_price[interval][-1] - self.ema[ema_window][interval][-1]) +
                self.ema[ema_window][interval][-1])


def _get_adx_sum(s, n):
    if ((n - 1) * 2 + 1) >= len(s):
        return s
    result = s.tolist()
    initial_sum = sum(s[n:(n - 1) * 2 + 1])
    result[(n - 1) * 2 + 1] = initial_sum
    for i in range(n * 2, len(s.index)):
        result[i] = (result[i - 1] * 13 + result[i]) / n
    return pd.Series(data=result, index=s.index)


def _get_ema_value(s, n):
    if n >= len(s.index):
        return pd.Series(data=0, index=s.index)
    initial_sum_value = s.rolling(window=n, min_periods=n).sum().get(n, 0)
    result = s.tolist()
    result[n] = initial_sum_value
    for i in range(n + 1, len(s.index)):
        result[i] = result[i - 1] - (result[i - 1] / n) + result[i]
    return pd.Series(data=result, index=s.index)


def _average_directional_movement_index(df, n):
    adx = df.loc[:, ['high', 'close', 'low']]
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
