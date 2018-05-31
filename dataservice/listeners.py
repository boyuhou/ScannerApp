import numpy as np
import collections, itertools
from dataservice.indicator import Ticker, calc_ewma_vectorized
from pyiqfeed.listeners import VerboseIQFeedListener


class QuoteListener(VerboseIQFeedListener):
    def __init__(self, name: str):
        super().__init__(name)
        self.data_dict = {
            'AUDCAD.FXCM': Ticker(),
            'AUDCHF.FXCM': Ticker(),
            'AUDJPY.FXCM': Ticker(),
            'AUDNZD.FXCM': Ticker(),
            'AUDUSD.FXCM': Ticker(),
            'CADCHF.FXCM': Ticker(),
            'CADJPY.FXCM': Ticker(),
            'CHFJPY.FXCM': Ticker(),
            'EURAUD.FXCM': Ticker(),
            'EURCAD.FXCM': Ticker(),
            'EURCHF.FXCM': Ticker(),
            'EURGBP.FXCM': Ticker(),
            'EURJPY.FXCM': Ticker(),
            'EURNZD.FXCM': Ticker(),
            'EURUSD.FXCM': Ticker(),
            'GBPAUD.FXCM': Ticker(),
            'GBPCAD.FXCM': Ticker(),
            'GBPCHF.FXCM': Ticker(),
            'GBPJPY.FXCM': Ticker(),
            'GBPNZD.FXCM': Ticker(),
            'GBPUSD.FXCM': Ticker(),
            'NZDCAD.FXCM': Ticker(),
            'NZDCHF.FXCM': Ticker(),
            'NZDJPY.FXCM': Ticker(),
            'NZDUSD.FXCM': Ticker(),
            'USDCAD.FXCM': Ticker(),
            'USDCHF.FXCM': Ticker(),
            'USDJPY.FXCM': Ticker(),
        }

    def process_latest_bar_update(self, bar_data: np.array) -> None:
        print("%s: Process latest bar update:" % self._name)
        close_price = bar_data['close_p'][0]
        high_price = bar_data['high_p'][0]
        low_price = bar_data['low_p'][0]
        open_price = bar_data['open_p'][0]
        quote_time = bar_data['datetime'][0]
        print('Datetime: {4}, Open: {0}, Close: {1}, High: {2}, Low: {3}'.format(open_price, close_price, high_price,
                                                                                 low_price, quote_time))
        min_interval = int(int(bar_data['id'][0].split('-')[2]) / 60)
        ticker = bar_data['symbol'][0]
        close_price = bar_data['close_p'][0]

        if quote_time == self.data_dict[ticker].time_list[min_interval][-1]:
            ema_08 = calc_ewma_vectorized(list(self.data_dict[ticker].bar_list[min_interval])[:-1] + [close_price],
                                          list(self.data_dict[ticker].ema_08[min_interval])[-2], window=8)
            ema_21 = calc_ewma_vectorized(list(self.data_dict[ticker].bar_list[min_interval])[:-1] + [close_price],
                                          list(self.data_dict[ticker].ema_21[min_interval])[-2], window=21)
            ema_50 = calc_ewma_vectorized(list(self.data_dict[ticker].bar_list[min_interval])[:-1] + [close_price],
                                          list(self.data_dict[ticker].ema_50[min_interval])[-2], window=50)
        else:
            pass

        self.data_dict[ticker].current_ema[min_interval] = {
            8: ema_08,
            21: ema_21,
            50: ema_50
        }
        print(self.data_dict[ticker].current_ema[min_interval])

    def process_live_bar(self, bar_data: np.array) -> None:
        print("%s: Process live bar:" % self._name)
        min_interval = int(int(bar_data['id'][0].split('-')[2]) / 60)
        ticker = bar_data['symbol'][0]
        close_price = bar_data['close_p'][0]
        quote_time = bar_data['datetime'][0]

        if min_interval not in self.data_dict[ticker].current_ema:
            raise KeyError('not supported mins')

        self.data_dict[ticker].bar_list[min_interval].append(close_price)
        self.data_dict[ticker].time_list[min_interval].append(quote_time)

        ema_08 = calc_ewma_vectorized(list(self.data_dict[ticker].bar_list[min_interval]),
                                      self.data_dict[ticker].ema_08[min_interval], window=8)
        ema_21 = calc_ewma_vectorized(list(self.data_dict[ticker].bar_list[min_interval]),
                                      self.data_dict[ticker].ema_21[min_interval], window=21)
        ema_50 = calc_ewma_vectorized(list(self.data_dict[ticker].bar_list[min_interval]),
                                      self.data_dict[ticker].ema_50[min_interval], window=50)

        self.data_dict[ticker].ema_08[min_interval].append(ema_08)
        self.data_dict[ticker].ema_21[min_interval].append(ema_21)
        self.data_dict[ticker].ema_50[min_interval].append(ema_50)
        self.data_dict[ticker].current_ema[min_interval] = {
            8: ema_08,
            21: ema_21,
            50: ema_50
        }

    def process_history_bar(self, bar_data: np.array) -> None:
        print("%s: Process history bar:" % self._name)
        print(bar_data)
        min_interval = int(int(bar_data['id'][0].split('-')[2]) / 60)
        ticker = bar_data['symbol'][0]
        close_price = bar_data['close_p'][0]
        quote_time = bar_data['datetime'][0]

        if min_interval not in self.data_dict[ticker].current_ema:
            raise KeyError('not supported mins')

        self.data_dict[ticker].bar_list[min_interval].append(close_price)
        self.data_dict[ticker].time_list[min_interval].append(quote_time)

        ema_08 = calc_ewma_vectorized(list(self.data_dict[ticker].bar_list[min_interval]),
                                      self.data_dict[ticker].ema_08[min_interval], window=8)
        ema_21 = calc_ewma_vectorized(list(self.data_dict[ticker].bar_list[min_interval]),
                                      self.data_dict[ticker].ema_21[min_interval], window=21)
        ema_50 = calc_ewma_vectorized(list(self.data_dict[ticker].bar_list[min_interval]),
                                      self.data_dict[ticker].ema_50[min_interval], window=50)

        self.data_dict[ticker].ema_08[min_interval].append(ema_08)
        self.data_dict[ticker].ema_21[min_interval].append(ema_21)
        self.data_dict[ticker].ema_50[min_interval].append(ema_50)
        self.data_dict[ticker].current_ema[min_interval] = {
            8: ema_08,
            21: ema_21,
            50: ema_50
        }
        print(self.data_dict[ticker].current_ema[min_interval])

    def process_invalid_symbol(self, bad_symbol: str) -> None:
        print("%s: Invalid Symbol: %s" % (self._name, bad_symbol))

    def process_symbol_limit_reached(self, symbol: str) -> None:
        print("%s: Symbol Limit reached: %s" % (self._name, symbol))

    def process_replaced_previous_watch(self, symbol: str) -> None:
        print("%s: Replaced previous watch: %s" % (self._name, symbol))

    def process_watch(self, symbol: str, interval: int, request_id: str):
        print("%s: Process watch: %s, %d, %s" %
              (self._name, symbol, interval, request_id))
