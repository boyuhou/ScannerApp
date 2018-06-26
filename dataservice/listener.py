from datetime import datetime
from typing import List

import numpy as np
from PyQt5 import Qt
from PyQt5.QtWidgets import QApplication

from dataservice.ticker import Ticker, Signals
from pyiqfeed.listeners import SilentBarListener
from ui.test import Ui_MainWindow


class QuoteListener(SilentBarListener):
    """
    Processor is a adapter between ui and tickers

    It maintains all the tickers data and update ui
    """

    def __init__(self, name: str, ui: Ui_MainWindow, tickers: [str], ui_app: QApplication, is_debug: bool = False):
        super().__init__(name)
        self.ui = ui
        self.tickers = tickers
        self.is_debug = is_debug
        self.ui_app = ui_app
        self.data_dict = {}
        self.callback_dict = {}
        for ticker in tickers:
            self.data_dict[ticker] = Ticker(ticker)
            self.callback_dict[ticker] = self.UIControlCallback(self, ticker)
        self.gui_callbacks = {
            1: self._update_gui_1min,
            5: self._update_gui_5min,
            15: self._update_gui_15min,
            60: self._update_gui_60min,
            240: self._update_gui_240min
        }
        self.system_tray_icon = Qt.QSystemTrayIcon(self.ui_app)
        self.system_tray_icon.show()

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
        self._update_text("tsi5_", ticker.name, ticker.trend_smooth_indicator[5][-1])
        self._update_text("emao5_", ticker.name, ticker.ema_order[5][-1], 0)
        self._update_bg_color("emao5_", ticker.name, self._get_watcher_bg_color(ticker.ema_order[5][-1]))

    def _update_gui_15min(self, ticker: Ticker) -> None:
        range_value = ticker.range[15][-1]
        self._update_text("range20min15_", ticker.name, range_value)
        self._update_bg_color("range20min15_", ticker.name, self._get_range15_bg_color(range_value))
        self._update_text("tsi15_", ticker.name, ticker.trend_smooth_indicator[15][-1])
        self._update_text("emao15_", ticker.name, ticker.ema_order[15][-1], 0)
        self._update_bg_color("emao15_", ticker.name, self._get_watcher_bg_color(ticker.ema_order[15][-1]))

    def _update_gui_60min(self, ticker: Ticker) -> None:
        self._update_text("tsi60_", ticker.name, ticker.trend_smooth_indicator[60][-1])
        self._update_text("emao60_", ticker.name, ticker.ema_order[60][-1], 0)
        self._update_bg_color("emao60_", ticker.name, self._get_watcher_bg_color(ticker.ema_order[60][-1]))

    def _update_gui_240min(self, ticker: Ticker) -> None:
        pass

    def _update_text(self, prefix: str, ticker_name: str, value: float, digits=4):
        label_name = prefix + ticker_name
        label = getattr(self.ui, label_name)
        label.setText(self._str(value, digits))

    def _update_bg_color(self, prefix: str, ticker_name: str, color: str):
        widget_name = prefix + ticker_name
        widget = getattr(self.ui, widget_name)
        widget.setStyleSheet("background-color: {}".format(color))

    @staticmethod
    def _get_watcher_bg_color(value: float) -> str:
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

    def update_gui_latest(self, ticker: Ticker):
        is_all_touched = True
        for watcher_name, is_touched in ticker.active_watchers.items():
            widget = self.callback_dict[ticker.full_name].signal_widget_dict[watcher_name]
            is_all_touched = is_touched and is_all_touched
            # if is_touched:
            #     widget.setStyleSheet("background-color: green")
            # else:
            #     widget.setStyleSheet("background-color: red")
        if (len(ticker.active_watchers.items()) > 0) and is_all_touched:
            self._show_popup(ticker.name)

    def _show_popup(self, ticker_name: str):
        self.system_tray_icon.showMessage('Ticker', ticker_name)

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

        ticker.update_latest_price(high_price, low_price, time_interval)
        self.update_gui_latest(ticker)
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

    @staticmethod
    def _str(number: float, digits=4) -> str:
        return '{number:.{digits}f}'.format(number=number, digits=digits)

    """
    GUI control callbacks
    """

    def btn_submit_callback(self, ticker_name: str, watcher_names: List[str]):
        ticker = self.data_dict[ticker_name]
        ticker.start_watch(watcher_names)

    def btn_cancel_callback(self, ticker_name: str):
        ticker = self.data_dict[ticker_name]
        ticker.stop_watch()

    class UIControlCallback:
        def __init__(self, outer_instance, name: str):
            self.full_name = name
            self.name = name.split(".")[0]
            self.outer_instance = outer_instance
            self.ui = outer_instance.ui
            self.ckb_p5ema50 = getattr(self.ui, 'ckb_p5ema50_' + self.name)
            self.ckb_p15ema21 = getattr(self.ui, 'ckb_p15ema21_' + self.name)
            self.ckb_p15ema50 = getattr(self.ui, 'ckb_p15ema50_' + self.name)
            self.ckb_p60ema8 = getattr(self.ui, 'ckb_p60ema8_' + self.name)
            self.ckb_p60ema21 = getattr(self.ui, 'ckb_p60ema21_' + self.name)
            self.ckb_p240ema8 = getattr(self.ui, 'ckb_p240ema8_' + self.name)
            self.checkboxes = {
                self.ckb_p5ema50: Signals.P5EMA50,
                self.ckb_p15ema21: Signals.P15EMA21,
                self.ckb_p15ema50: Signals.P15EMA50,
                self.ckb_p60ema8: Signals.P60EMA8,
                self.ckb_p60ema21: Signals.P60EMA21,
                self.ckb_p240ema8: Signals.P240EMA8
            }
            self.signal_widget_dict = {
                Signals.P5EMA50: self.ckb_p5ema50,
                Signals.P15EMA21: self.ckb_p15ema21,
                Signals.P15EMA50: self.ckb_p15ema50,
                Signals.P60EMA8: self.ckb_p60ema8,
                Signals.P60EMA21: self.ckb_p60ema21,
                Signals.P240EMA8: self.ckb_p240ema8
            }
            self.btn_submit = getattr(self.ui, 'submit_' + self.name)
            self.btn_cancel = getattr(self.ui, 'cancel_' + self.name)

            self.btn_submit.clicked.connect(self.btn_submit_callback)
            self.btn_cancel.clicked.connect(self.btn_cancel_callback)

        def btn_submit_callback(self):
            watchers = []
            for checkbox, name in self.checkboxes.items():
                if checkbox.isChecked():
                    checkbox.setEnabled(False)
                    watchers.append(name)
            self.outer_instance.btn_submit_callback(self.full_name, watchers)

        def btn_cancel_callback(self):
            for checkbox in self.checkboxes.keys():
                checkbox.setChecked(False)
                checkbox.setEnabled(True)
                checkbox.setStyleSheet("background-color: none")
            self.outer_instance.btn_cancel_callback(self.full_name)
