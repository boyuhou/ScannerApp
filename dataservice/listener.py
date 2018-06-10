import numpy as np

from dataservice.ticker import Ticker
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
        self.gui_callbacks = {
            1: self._update_gui_1min,
            5: self._update_gui_5min,
            15: self._update_gui_15min,
            60: self._update_gui_60min,
            240: self._update_gui_240min
        }

    """
    GUI callbacks
    """

    def update_gui(self, ticker: Ticker, interval: int) -> None:
        self.gui_callbacks[interval](ticker)

    def _update_gui_1min(self, ticker: Ticker) -> None:
        pass

    def _update_gui_5min(self, ticker: Ticker) -> None:
        self._update_text("range20min5_", ticker.name, ticker.range[5][-1])
        self._update_text("tsi5_", ticker.name, ticker.trend_smooth_indicator[5][-1])

    def _update_gui_15min(self, ticker: Ticker) -> None:
        self._update_text("range20min15_", ticker.name, ticker.range[15][-1])
        self._update_text("tsi15_", ticker.name, ticker.trend_smooth_indicator[15][-1])

    def _update_gui_60min(self, ticker: Ticker) -> None:
        self._update_text("tsi60_", ticker.name, ticker.trend_smooth_indicator[60][-1])

    def _update_gui_240min(self, ticker: Ticker) -> None:
        pass

    def _update_text(self, prefix: str, ticker_name: str, value: float):
        label_name = prefix + ticker_name
        label = getattr(self.ui, label_name)
        label.setText(self._str(value))

    """
    Listener callbacks
    """

    def process_latest_bar_update(self, bar_data: np.array) -> None:
        if self.is_debug:
            print("Process latest bar update: ", bar_data)
        time_interval = int(int(bar_data['id'][0].split('-')[2]) / 60)
        name = bar_data['symbol'][0]
        open_price = bar_data['open_p'][0]
        high_price = bar_data['high_p'][0]
        low_price = bar_data['low_p'][0]
        close_price = bar_data['close_p'][0]
        quote_time = bar_data['datetime'][0]
        ticker = self.data_dict[name]

        ticker.insert_new_price(time_interval, open_price, high_price, low_price, close_price, quote_time)
        ticker.update_indicator(time_interval)
        self.update_gui(ticker, time_interval)

    def process_live_bar(self, bar_data: np.array) -> None:
        if self.is_debug:
            print("Process live bar: ", bar_data)

    def process_history_bar(self, bar_data: np.array) -> None:
        if self.is_debug:
            print("Process history bar: ", bar_data)

        time_interval = int(int(bar_data['id'][0].split('-')[2]) / 60)
        name = bar_data['symbol'][0]
        open_price = bar_data['open_p'][0]
        high_price = bar_data['high_p'][0]
        low_price = bar_data['low_p'][0]
        close_price = bar_data['close_p'][0]
        quote_time = bar_data['datetime'][0]
        ticker = self.data_dict[name]
        
        ticker.insert_new_price(time_interval, open_price, high_price, low_price, close_price, quote_time)
        ticker.update_indicator(time_interval)

    @staticmethod
    def _str(number: float) -> str:
        return '{number:.{digits}f}'.format(number=number, digits=4)
