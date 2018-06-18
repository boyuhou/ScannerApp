import numpy as np

from dataservice.ticker import Ticker, Signals
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

    def add_watcher_callback(self, ticker_name: str, watcher_name: str):
        ticker = self.data_dict[ticker_name]
        ticker.add_watcher(watcher_name)

    def remove_watcher_callback(self, ticker_name: str, watcher_name: str):
        ticker = self.data_dict[ticker_name]
        ticker.remove_watcher(watcher_name)

    def btn_submit_callback(self, ticker_name: str):
        ticker = self.data_dict[ticker_name]
        ticker.start_watch()

    def btn_cancel_callback(self, ticker_name: str):
        ticker = self.data_dict[ticker_name]
        ticker.stop_watch()

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
        self._update_text("emao5_", ticker.name, ticker.ema_order[5][-1], 0)

    def _update_gui_15min(self, ticker: Ticker) -> None:
        self._update_text("range20min15_", ticker.name, ticker.range[15][-1])
        self._update_text("tsi15_", ticker.name, ticker.trend_smooth_indicator[15][-1])
        self._update_text("emao15_", ticker.name, ticker.ema_order[15][-1], 0)

    def _update_gui_60min(self, ticker: Ticker) -> None:
        self._update_text("tsi60_", ticker.name, ticker.trend_smooth_indicator[60][-1])
        self._update_text("emao60_", ticker.name, ticker.ema_order[60][-1], 0)

    def _update_gui_240min(self, ticker: Ticker) -> None:
        pass

    def _update_text(self, prefix: str, ticker_name: str, value: float, digits=4):
        label_name = prefix + ticker_name
        label = getattr(self.ui, label_name)
        label.setText(self._str(value, digits))

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
    def _str(number: float, digits=4) -> str:
        return '{number:.{digits}f}'.format(number=number, digits=digits)

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
            self.btn_submit = getattr(self.ui, 'submit_' + self.name)
            self.btn_cancel = getattr(self.ui, 'cancel_' + self.name)

            self.ckb_p5ema50.stateChanged.connect(self.p5ema50_callback)
            self.ckb_p15ema21.stateChanged.connect(self.p15ema21_callback)
            self.ckb_p15ema50.stateChanged.connect(self.p15ema50_callback)
            self.ckb_p60ema8.stateChanged.connect(self.p60ema8_callback)
            self.ckb_p60ema21.stateChanged.connect(self.p60ema21_callback)
            self.ckb_p240ema8.stateChanged.connect(self.p240ema8_callback)
            self.btn_submit.clicked.connect(self.btn_submit_callback)
            self.btn_cancel.clicked.connect(self.btn_cancel_callback)

        def p5ema50_callback(self):
            if self.ckb_p5ema50.isChecked():
                self.outer_instance.add_watcher_callback(self.full_name, Signals.P5EMA50)
            else:
                self.outer_instance.remove_watcher_callback(self.full_name, Signals.P5EMA50)

        def p15ema21_callback(self):
            if self.ckb_p15ema21.isChecked():
                self.outer_instance.add_watcher_callback(self.full_name, Signals.P15EMA21)
            else:
                self.outer_instance.remove_watcher_callback(self.full_name, Signals.P15EMA21)

        def p15ema50_callback(self):
            if self.ckb_p15ema50.isChecked():
                self.outer_instance.add_watcher_callback(self.full_name, Signals.P15EMA50)
            else:
                self.outer_instance.remove_watcher_callback(self.full_name, Signals.P15EMA50)

        def p60ema8_callback(self):
            if self.ckb_p60ema8.isChecked():
                self.outer_instance.add_watcher_callback(self.full_name, Signals.P60EMA8)
            else:
                self.outer_instance.remove_watcher_callback(self.full_name, Signals.P60EMA8)

        def p60ema21_callback(self):
            if self.ckb_p60ema21.isChecked():
                self.outer_instance.add_watcher_callback(self.full_name, Signals.P60EMA21)
            else:
                self.outer_instance.remove_watcher_callback(self.full_name, Signals.P60EMA21)

        def p240ema8_callback(self):
            if self.ckb_p240ema8.isChecked():
                self.outer_instance.add_watcher_callback(self.full_name, Signals.P240EMA8)
            else:
                self.outer_instance.remove_watcher_callback(self.full_name, Signals.P240EMA8)

        def btn_submit_callback(self):
            self.outer_instance.btn_submit_callback(self.full_name)

        def btn_cancel_callback(self):
            self.ckb_p5ema50.setChecked(False)
            self.ckb_p15ema21.setChecked(False)
            self.ckb_p15ema50.setChecked(False)
            self.ckb_p60ema8.setChecked(False)
            self.ckb_p60ema21.setChecked(False)
            self.ckb_p240ema8.setChecked(False)
            self.outer_instance.btn_cancel_callback(self.full_name)
