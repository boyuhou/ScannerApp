import numpy as np

from dataservice.indicator import Ticker
from pyiqfeed.listeners import SilentBarListener
from ui.test import Ui_Dialog


class QuoteListener(SilentBarListener):

    """
    Processor is a adapter between ui and tickers

    It maintains all the tickers data and update ui
    """

    def __init__(self, name: str, ui: Ui_Dialog, tickers: [str], is_debug: bool = False):
        super().__init__(name)
        self.ui = ui
        self.tickers = tickers
        self.is_debug = is_debug
        self.data_dict = {}
        for ticker in tickers:
            self.data_dict[ticker] = Ticker(ticker)

    """
    Listener callbacks
    """
    def process_latest_bar_update(self, bar_data: np.array) -> None:
        if self.is_debug:
            print("Process latest bar update: ", bar_data)

    def process_live_bar(self, bar_data: np.array) -> None:
        if self.is_debug:
            print("Process live bar: ", bar_data)

    def process_history_bar(self, bar_data: np.array) -> None:
        if self.is_debug:
            print("Process history bar: ", bar_data)

        time_interval = int(int(bar_data['id'][0].split('-')[2]) / 60)
        ticker = bar_data['symbol'][0]
        open_price = bar_data['open_p'][0]
        high_price = bar_data['high_p'][0]
        low_price = bar_data['low_p'][0]
        close_price = bar_data['close_p'][0]
        quote_time = bar_data['datetime'][0]

        self.data_dict[ticker].insert_new_price(time_interval, open_price, high_price, low_price, close_price, quote_time)
        self.data_dict[ticker].update_indicator(time_interval)

