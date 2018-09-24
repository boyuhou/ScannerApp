from datetime import datetime
from typing import List

import numpy as np

from dataservice.ticker import Ticker, RL_WATCHERS
from pyiqfeed.listeners import SilentBarListener
from ui.ui import ScannerUI


class QuoteListener(SilentBarListener):
    """
    Processor is a adapter between ui and tickers

    It maintains all the tickers data and update ui
    """

    def __init__(self, name: str, ui: ScannerUI, tickers: [str], is_debug: bool = False):
        super().__init__(name)
        self.ui = ui
        self.tickers = tickers
        self.is_debug = is_debug
        self.data_dict = {}
        self.callback_dict = {}
        for ticker in tickers:
            self.data_dict[ticker] = Ticker(ticker)
        self.ui.set_callback(self)
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
        range_value = ticker.range[5][-1]
        self._update_text("range20min5_", ticker.name, range_value)
        self._update_bg_color("range20min5_", ticker.name, self._get_range5_bg_color(range_value))
        # self._update_text("tsi5_", ticker.name, ticker.trend_smooth_indicator[5][-1])
        self._update_text("emao5_", ticker.name, ticker.ema_order[5][-1], 0)
        self._update_bg_color("emao5_", ticker.name, self._get_ema_order_bg_color(ticker.ema_order[5][-1]))

    def _update_gui_15min(self, ticker: Ticker) -> None:
        range_value = ticker.range[15][-1]
        self._update_text("range20min15_", ticker.name, range_value)
        self._update_bg_color("range20min15_", ticker.name, self._get_range15_bg_color(range_value))
        # self._update_text("tsi15_", ticker.name, ticker.trend_smooth_indicator[15][-1])
        self._update_text("emao15_", ticker.name, ticker.ema_order[15][-1], 0)
        self._update_bg_color("emao15_", ticker.name, self._get_ema_order_bg_color(ticker.ema_order[15][-1]))

    def _update_gui_60min(self, ticker: Ticker) -> None:
        # self._update_text("tsi60_", ticker.name, ticker.trend_smooth_indicator[60][-1])
        self._update_text("emao60_", ticker.name, ticker.ema_order[60][-1], 0)
        self._update_bg_color("emao60_", ticker.name, self._get_ema_order_bg_color(ticker.ema_order[60][-1]))

    def _update_gui_240min(self, ticker: Ticker) -> None:
        pass

    def _update_text(self, prefix: str, ticker_name: str, value: float, digits=2):
        label_name = prefix + ticker_name
        self.ui.on_label_change(label_name, self._str(value, digits))

    def _update_bg_color(self, prefix: str, ticker_name: str, color: str):
        widget_name = prefix + ticker_name
        self.ui.on_bg_color_change(widget_name, color)

    @staticmethod
    def _get_ema_order_bg_color(value: float) -> str:
        if value == 1:
            return "green"
        elif value == -1:
            return "red"
        else:
            return "none"

    @staticmethod
    def _get_range5_bg_color(value: float) -> str:
        if value <= 7:
            return "green"
        elif value <= 14:
            return "yellow"
        elif value >= 21:
            return "red"
        else:
            return "none"

    @staticmethod
    def _get_range15_bg_color(value: float) -> str:
        if value <= 14:
            return "green"
        elif value <= 21:
            return "yellow"
        else:
            return "none"

    @staticmethod
    def _str(number: float, digits=4) -> str:
        return '{number:.{digits}f}'.format(number=number, digits=digits)

    def update_gui_latest(self, ticker: Ticker, watcher_names: [str]):
        rl_watcher_names = []
        for watcher_name in watcher_names:
            if watcher_name in RL_WATCHERS:
                rl_watcher_names.append(watcher_name)
            else:
                self.ui.on_watcher_color_change(ticker.name, watcher_name, "green")
        if len(watcher_names) > 0:
            for watcher_group in ticker.watcher_groups:
                for watcher in watcher_group.watchers:
                    if watcher.name in rl_watcher_names:
                        self.ui.on_watcher_color_change(ticker.name, watcher.name,
                                                        "green" if watcher.is_rl_up() else "red")
                if watcher_group.is_show_popup:
                    self.ui.show_popup(ticker.name, watcher_group.message)

    """
    Listener callbacks
    """

    def process_latest_bar_update(self, bar_data: np.array) -> None:
        if self.is_debug:
            print("Process latest bar: ", bar_data)
        name = bar_data['symbol'][0]
        high_price = bar_data['high_p'][0]
        low_price = bar_data['low_p'][0]
        time_interval = int(int(bar_data['id'][0].split('-')[2]) / 60)
        ticker = self.data_dict[name]

        watcher_names = ticker.update_latest_price(high_price, low_price, time_interval)
        self.update_gui_latest(ticker, watcher_names)
        # Init GUI if necessary
        if not ticker.is_ui_loaded:
            for interval in self.gui_callbacks.keys():
                self.update_gui(ticker, interval)
            ticker.is_ui_loaded = True

    def process_live_bar(self, bar_data: np.array) -> None:
        if self.is_debug:
            print("Process live bar update: ", bar_data)
        time_interval = int(int(bar_data['id'][0].split('-')[2]) / 60)
        name = bar_data['symbol'][0]
        open_price = bar_data['open_p'][0]
        high_price = bar_data['high_p'][0]
        low_price = bar_data['low_p'][0]
        close_price = bar_data['close_p'][0]
        ticker = self.data_dict[name]

        ticker.insert_new_price(time_interval, open_price, high_price, low_price, close_price)
        ticker.update_indicator(time_interval)
        self.update_gui(ticker, time_interval)

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

        if datetime.now() >= datetime.strptime(quote_time, "%Y-%m-%d %H:%M:%S"):
            ticker.insert_new_price(time_interval, open_price, high_price, low_price, close_price)
            ticker.update_indicator(time_interval)

    """
    GUI control callbacks
    """

    def btn_submit_callback(self, ticker_name: str, watcher_names: List[str], message: str, fixed_price: float):
        ticker = self.data_dict[ticker_name + '.FXCM']
        ticker.start_watch(watcher_names, message, fixed_price)

    def btn_cancel_callback(self, ticker_name: str):
        ticker = self.data_dict[ticker_name + '.FXCM']
        ticker.stop_watch()
