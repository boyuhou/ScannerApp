import collections
from typing import List

import numpy as np
import pandas as pd

TSI_PERIOD = 200


class Ticker:
    def __init__(self, name: str):
        self.full_name = name
        self.name = name.split(".")[0]
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
        self.ema_order = {
            5: collections.deque(maxlen=TSI_PERIOD),
            15: collections.deque(maxlen=TSI_PERIOD),
            60: collections.deque(maxlen=TSI_PERIOD),
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
        self.range = {
            5: collections.deque(maxlen=TSI_PERIOD),
            15: collections.deque(maxlen=TSI_PERIOD)
        }
        self.watcher_groups: [WatcherGroup] = []
        self.is_ui_loaded = False
        self.multiplier = 100.0 if 'JPY' in self.name else 10000.0
        # self.message = ""
        # self.watchers_price = {
        #     Watchers.P5EMA50: self.ema[5][50],
        #     Watchers.P15EMA21: self.ema[15][21],
        #     Watchers.P15EMA50: self.ema[15][50],
        #     Watchers.P60EMA8: self.ema[60][8],
        #     Watchers.P60EMA21: self.ema[60][21],
        #     Watchers.P240EMA8: self.ema[240][8],
        #     Watchers.PRICE_TOUCHE: -1.0
        # }

    def insert_new_price(self, time_interval: int, open_p: float, high_p: float, low_p: float, close_p: float) -> None:
        self.close_price[time_interval].append(close_p)
        self.open_price[time_interval].append(open_p)
        self.low_price[time_interval].append(low_p)
        self.high_price[time_interval].append(high_p)

    def update_indicator(self, interval) -> None:
        self._update_all_ema(interval)
        self._update_ema_order(interval)
        self._update_price_change(interval)
        self._update_tsi(interval)
        self._update_range20(interval)

    def update_latest_price(self, high_p: float, low_p: float, time_interval: int) -> [str]:
        result: [str] = []
        for watcher_group in self.watcher_groups:
            group_result = watcher_group.update(high_p, low_p, time_interval)
            result.extend(group_result)
        return result

    def start_watch(self, watcher_names: List[str], message: str, fixed_price: float):
        watcher_group = WatcherGroup(self, watcher_names=watcher_names, message=message, fixed_price=fixed_price)
        self.watcher_groups.append(watcher_group)
        print('{} started watching {}'.format(self.name, watcher_names))

    def stop_watch(self):
        self.watcher_groups = []
        print('{} stopped watching'.format(self.name))

    def _update_all_ema(self, interval: int) -> None:
        self._update_ema(interval, ema_window=8)
        self._update_ema(interval, ema_window=21)
        self._update_ema(interval, ema_window=50)

    def _update_range20(self, interval: int) -> None:
        if interval != 5 and interval != 15:
            return
        if (len(self.high_price[interval]) < 20) or (len(self.low_price[interval]) < 20):
            self.range[interval].append(np.nan)
        else:
            interval_range = max(list(self.close_price[interval])[-20:]) - min(list(self.close_price[interval])[-20:])
            self.range[interval].append(interval_range * self.multiplier)

    def _update_price_change(self, interval: int):
        if len(self.close_price[interval]) < 2:
            self.price_change[interval].append(np.nan)
        else:
            self.price_change[interval].append(
                (self.close_price[interval][-1] - self.close_price[interval][-2]) / self.close_price[interval][-2])

    def _update_tsi(self, interval: int):
        if len(self.price_change[interval]) < TSI_PERIOD:
            self.trend_smooth_indicator[interval].append(np.nan)
        else:
            close_array = np.asarray(self.price_change[interval])
            mean = np.mean(close_array)
            std = np.std(close_array)
            self.trend_smooth_indicator[interval].append(mean / std * 10.)

    def _update_ema(self, interval: int, ema_window: int) -> None:
        if len(self.close_price[interval]) < ema_window:
            self.ema[ema_window][interval].append(
                _numpy_ewma_vectorized(np.asarray(self.close_price[interval]), ema_window))
        else:
            self.ema[ema_window][interval].append(
                2. / (ema_window + 1) * (self.close_price[interval][-1] - self.ema[ema_window][interval][-1]) +
                self.ema[ema_window][interval][-1])

    def _update_ema_order(self, interval: int) -> None:
        if interval != 5 and interval != 15 and interval != 60:
            return
        if len(self.close_price[interval]) < 50:
            self.ema_order[interval].append(np.nan)
            return

        ema8 = list(self.ema[8][interval])[-1]
        ema21 = list(self.ema[21][interval])[-1]
        ema50 = list(self.ema[50][interval])[-1]
        if (ema8 > ema21) and (ema21 > ema50):
            self.ema_order[interval].append(1)
        elif (ema8 < ema21) and (ema21 < ema50):
            self.ema_order[interval].append(-1)
        else:
            self.ema_order[interval].append(0)


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


def _numpy_ewma_vectorized(data, window):
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


class Watchers:
    P5EMA50 = 'p5ema50'
    P15EMA21 = 'p15ema21'
    P15EMA50 = 'p15ema50'
    P60EMA8 = 'p60ema8'
    P60EMA21 = 'p60ema21'
    P240EMA8 = 'p240ema8'
    PRICE_TOUCHE = 'price_touch'


WATCHER_PERIOD_DICT = {
    Watchers.P5EMA50: (5, 50),
    Watchers.P15EMA21: (15, 21),
    Watchers.P15EMA50: (15, 50),
    Watchers.P60EMA8: (60, 8),
    Watchers.P60EMA21: (60, 21),
    Watchers.P240EMA8: (240, 8),

}


class Watcher:

    def __init__(self, name: str, ticker: Ticker, fixed_price: float = None, ema_period: int = None,
                 price_period: int = None):
        self.name = name
        self.ticker = ticker
        self.fixed_price = fixed_price
        self.ema_period = ema_period
        self.price_period = price_period
        self.is_fixed_price = True if fixed_price is not None else False
        self.is_touched = False

    def update(self, high: float, low: float) -> None:
        if self.is_touched:
            return

        self.is_touched = self._update_is_touched(high, low, self.fixed_price) if self.is_fixed_price \
            else self._update_is_touched(high, low, list(self.ticker.ema[self.ema_period][self.price_period])[-1])

    @staticmethod
    def _update_is_touched(high: float, low: float, price: float) -> bool:
        return (high > price) and (price > low)


class WatcherGroup:

    def __init__(self, ticker: Ticker, watcher_names: [int], fixed_price: float, message: str = ""):
        self.ticker = ticker
        self.message = message
        self.watchers = []
        self.watcher_dict = {}
        self.is_all_touched = False
        self.is_show_popup = False
        for watcher_name in watcher_names:
            if watcher_name == Watchers.PRICE_TOUCHE:
                watcher = Watcher(name=watcher_name, ticker=self.ticker, fixed_price=fixed_price)
            else:
                ema_price_period = WATCHER_PERIOD_DICT[watcher_name]
                watcher = Watcher(name=watcher_name, ticker=self.ticker, ema_period=ema_price_period[1],
                                  price_period=ema_price_period[0])
            self.watchers.append(watcher)
            self.watcher_dict[watcher] = False

    def update(self, high: float, low: float, timer_interval: int) -> [str]:
        self.is_show_popup = False
        result = []
        for watcher in self.watchers:
            if watcher.is_fixed_price and timer_interval == 1:
                watcher.update(high, low)
            elif watcher.price_period == timer_interval:
                watcher.update(high, low)
            if watcher.is_touched != self.watcher_dict[watcher]:
                result.append(watcher.name)
                self.watcher_dict[watcher] = True

        if not self.is_show_popup:
            is_all_touched = True
            for watcher in self.watchers:
                is_all_touched = is_all_touched and watcher.is_touched
            if is_all_touched:
                self.is_show_popup = True

        return result
