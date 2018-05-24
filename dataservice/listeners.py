import numpy as np

from dataservice.indicator import Ticker
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
        print(bar_data)

    def process_live_bar(self, bar_data: np.array) -> None:
        print("%s: Process live bar:" % self._name)
        print(bar_data)

    def process_history_bar(self, bar_data: np.array) -> None:
        print("%s: Process history bar:" % self._name)
        print(bar_data)

    def process_invalid_symbol(self, bad_symbol: str) -> None:
        print("%s: Invalid Symbol: %s" % (self._name, bad_symbol))

    def process_symbol_limit_reached(self, symbol: str) -> None:
        print("%s: Symbol Limit reached: %s" % (self._name, symbol))

    def process_replaced_previous_watch(self, symbol: str) -> None:
        print("%s: Replaced previous watch: %s" % (self._name, symbol))

    def process_watch(self, symbol: str, interval: int, request_id: str):
        print("%s: Process watch: %s, %d, %s" %
              (self._name, symbol, interval, request_id))
