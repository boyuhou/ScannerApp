from typing import Callable

import numpy as np

from dataservice.indicator import Ticker
from pyiqfeed.listeners import VerboseIQFeedListener


class QuoteListener(VerboseIQFeedListener):
    def __init__(self, name: str, callback: Callable):
        super().__init__(name)
        self.data_dict = {
            'AUDCAD.FXCM': Ticker('AUDCAD.FXCM'),
            'AUDCHF.FXCM': Ticker('AUDCHF.FXCM'),
            'AUDJPY.FXCM': Ticker('AUDJPY.FXCM'),
            'AUDNZD.FXCM': Ticker('AUDNZD.FXCM'),
            'AUDUSD.FXCM': Ticker('AUDUSD.FXCM'),
            'CADCHF.FXCM': Ticker('CADCHF.FXCM'),
            'CADJPY.FXCM': Ticker('CADJPY.FXCM'),
            'CHFJPY.FXCM': Ticker('CHFJPY.FXCM'),
            'EURAUD.FXCM': Ticker('EURAUD.FXCM'),
            'EURCAD.FXCM': Ticker('EURCAD.FXCM'),
            'EURCHF.FXCM': Ticker('EURCHF.FXCM'),
            'EURGBP.FXCM': Ticker('EURGBP.FXCM'),
            'EURJPY.FXCM': Ticker('EURJPY.FXCM'),
            'EURNZD.FXCM': Ticker('EURNZD.FXCM'),
            'EURUSD.FXCM': Ticker('EURUSD.FXCM'),
            'GBPAUD.FXCM': Ticker('GBPAUD.FXCM'),
            'GBPCAD.FXCM': Ticker('GBPCAD.FXCM'),
            'GBPCHF.FXCM': Ticker('GBPCHF.FXCM'),
            'GBPJPY.FXCM': Ticker('GBPJPY.FXCM'),
            'GBPNZD.FXCM': Ticker('GBPNZD.FXCM'),
            'GBPUSD.FXCM': Ticker('GBPUSD.FXCM'),
            'NZDCAD.FXCM': Ticker('NZDCAD.FXCM'),
            'NZDCHF.FXCM': Ticker('NZDCHF.FXCM'),
            'NZDJPY.FXCM': Ticker('NZDJPY.FXCM'),
            'NZDUSD.FXCM': Ticker('NZDUSD.FXCM'),
            'USDCAD.FXCM': Ticker('USDCAD.FXCM'),
            'USDCHF.FXCM': Ticker('USDCHF.FXCM'),
            'USDJPY.FXCM': Ticker('USDJPY.FXCM'),
        }
        self.callback = callback

    def process_latest_bar_update(self, bar_data: np.array) -> None:
        print("%s: Process latest bar update:" % self._name)
        print(bar_data)
        self.callback(bar_data)
        # min_interval = int(int(bar_data['id'][0].split('-')[2]) / 60)
        # ticker = bar_data['symbol'][0]
        # close_price = bar_data['close_p'][0]
        # high_price = bar_data['high_p'][0]
        # low_price = bar_data['low_p'][0]
        # open_price = bar_data['open_p'][0]
        # quote_time = bar_data['datetime'][0]
        # print('Datetime: {4}, Open: {0}, Close: {1}, High: {2}, Low: {3}'.format(open_price, close_price, high_price,
        #                                                                          low_price, quote_time))

    def process_live_bar(self, bar_data: np.array) -> None:
        print("%s: Process live bar:" % self._name)
        print(bar_data)
        # min_interval = int(int(bar_data['id'][0].split('-')[2]) / 60)
        # ticker = bar_data['symbol'][0]
        # close_price = bar_data['close_p'][0]
        # quote_time = bar_data['datetime'][0]
        #
        # if min_interval not in self.data_dict[ticker].current_ema:
        #     raise KeyError('not supported mins')
        #
        # self.data_dict[ticker].bar_list[min_interval].append(close_price)
        # self.data_dict[ticker].time_list[min_interval].append(quote_time)
        #
        # ema_08 = numpy_ewma_vectorized(np.asarray(self.data_dict[ticker].bar_list[min_interval]), window=8)
        # ema_21 = numpy_ewma_vectorized(np.asarray(self.data_dict[ticker].bar_list[min_interval]), window=21)
        # ema_50 = numpy_ewma_vectorized(np.asarray(self.data_dict[ticker].bar_list[min_interval]), window=50)
        #
        # self.data_dict[ticker].ema_08[min_interval].append(ema_08)
        # self.data_dict[ticker].ema_21[min_interval].append(ema_21)
        # self.data_dict[ticker].ema_50[min_interval].append(ema_50)
        # self.data_dict[ticker].current_ema[min_interval] = {
        #     8: ema_08,
        #     21: ema_21,
        #     50: ema_50
        # }

    def process_history_bar(self, bar_data: np.array) -> None:
        print("%s: Process history bar:" % self._name)
        print(bar_data)
        time_interval = int(int(bar_data['id'][0].split('-')[2]) / 60)
        ticker = bar_data['symbol'][0]
        open_price = bar_data['open_p'][0]
        high_price = bar_data['high_p'][0]
        low_price = bar_data['low_p'][0]
        close_price = bar_data['close_p'][0]
        quote_time = bar_data['datetime'][0]

        self.data_dict[ticker].insert_new_price(time_interval, open_price, high_price, low_price, close_price, quote_time)
        self.data_dict[ticker].update_indicator(time_interval)

    def process_invalid_symbol(self, bad_symbol: str) -> None:
        print("%s: Invalid Symbol: %s" % (self._name, bad_symbol))

    def process_symbol_limit_reached(self, symbol: str) -> None:
        print("%s: Symbol Limit reached: %s" % (self._name, symbol))

    def process_replaced_previous_watch(self, symbol: str) -> None:
        print("%s: Replaced previous watch: %s" % (self._name, symbol))

    def process_watch(self, symbol: str, interval: int, request_id: str):
        print("%s: Process watch: %s, %d, %s" %
              (self._name, symbol, interval, request_id))
