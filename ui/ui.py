from PyQt5 import Qt
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QObject
from PyQt5.QtWidgets import QApplication

from dataservice.ticker import Watchers
from ui.ui_main_window import Ui_MainWindow


class ScannerUI(Ui_MainWindow, QObject):
    set_label_text_signal = pyqtSignal(str, str)
    set_widget_bg_color_signal = pyqtSignal(str, str)
    set_widget_enabled_signal = pyqtSignal(str, bool)
    set_checkbox_checked_signal = pyqtSignal(str, bool)

    def __init__(self, tickers: [str], ui_app: QApplication, is_debug: bool = False):
        super(ScannerUI, self).__init__()
        self.ticker_full_names = tickers
        self.ui_app = ui_app
        self.is_debug = is_debug
        self.listener = None
        self.ticker_components_group_dict = {}
        self._make_connection()

        self.system_tray_icon = Qt.QSystemTrayIcon(self.ui_app)
        self.system_tray_icon.show()

    def setupUi(self, main_window):
        super(ScannerUI, self).setupUi(main_window)
        self._init_components_groups()

    def _make_connection(self):
        self.set_label_text_signal.connect(self.set_widget_text)
        self.set_widget_bg_color_signal.connect(self.set_widget_bg_color)
        self.set_widget_enabled_signal.connect(self.set_widget_enabled)
        self.set_checkbox_checked_signal.connect(self.set_checkbox_checked)

    def _init_components_groups(self):
        self.ticker_control_dict = {}
        for ticker_full_name in self.ticker_full_names:
            ticker_name = ticker_full_name.split(".")[0]
            self.ticker_components_group_dict[ticker_name] = ControlWidgetGroup(ticker_name, self)

    @pyqtSlot(str, str)
    def set_widget_text(self, widget_name: str, value: str):
        label = getattr(self, widget_name)
        label.setText(value)

    @pyqtSlot(str, str)
    def set_widget_bg_color(self, widget_name: str, color: str):
        widget = getattr(self, widget_name)
        widget.setStyleSheet("background-color: {}".format(color))

    @pyqtSlot(str, bool)
    def set_widget_enabled(self, widget_name: str, enabled: bool):
        widget = getattr(self, widget_name)
        widget.setEnabled(enabled)

    @pyqtSlot(str, bool)
    def set_checkbox_checked(self, widget_name: str, checked: bool):
        widget = getattr(self, widget_name)
        widget.setChecked(checked)

    def on_label_change(self, widget_name: str, value: str):
        self.set_label_text_signal.emit(widget_name, value)

    def on_bg_color_change(self, widget_name: str, color: str):
        self.set_widget_bg_color_signal.emit(widget_name, color)

    def on_set_widget_enabled(self, widget_name: str, enabled: bool):
        self.set_widget_enabled_signal.emit(widget_name, enabled)

    def on_set_checkbox_checked(self, checkbox_name: str, checked: bool):
        self.set_checkbox_checked_signal.emit(checkbox_name, checked)

    def on_watcher_color_change(self, ticker_name: str, watcher: Watchers, color: str):
        widget_name = self.ticker_components_group_dict[ticker_name].get_get_widget_name(watcher)
        self.on_bg_color_change(widget_name, color)

    def set_callback(self, listener):
        self.listener = listener

    def submit_callback(self, ticker_name: str, watchers: [str], message: str, fixed_price: float):
        if self.is_debug:
            print(ticker_name, watchers, message, fixed_price)
        self.listener.btn_submit_callback(ticker_name, watchers, message, fixed_price)

    def cancel_callback(self, ticker_name: str):
        if self.is_debug:
            print(ticker_name)
        self.listener.btn_cancel_callback(ticker_name)

    def show_popup(self, ticker_name: str, message: str):
        self.system_tray_icon.showMessage(ticker_name, message)


class ControlWidgetGroup:

    def __init__(self, ticker_name: str, scanner_ui: ScannerUI):
        self.ticker_name = ticker_name
        self.scanner_ui = scanner_ui
        self.ckb_p5ema8 = getattr(self.scanner_ui, 'ckb_p5ema8_' + self.ticker_name)
        self.ckb_p5ema21 = getattr(self.scanner_ui, 'ckb_p5ema21_' + self.ticker_name)
        self.ckb_p5ema50 = getattr(self.scanner_ui, 'ckb_p5ema50_' + self.ticker_name)
        self.ckb_p15ema8 = getattr(self.scanner_ui, 'ckb_p15ema8_' + self.ticker_name)
        self.ckb_p15ema21 = getattr(self.scanner_ui, 'ckb_p15ema21_' + self.ticker_name)
        self.ckb_p15ema50 = getattr(self.scanner_ui, 'ckb_p15ema50_' + self.ticker_name)
        self.ckb_p60ema8 = getattr(self.scanner_ui, 'ckb_p60ema8_' + self.ticker_name)
        self.ckb_p60ema21 = getattr(self.scanner_ui, 'ckb_p60ema21_' + self.ticker_name)
        # self.ckb_p240ema8 = getattr(self.scanner_ui, 'ckb_p240ema8_' + self.ticker_name)
        self.ckb_price_touch = getattr(self.scanner_ui, 'ckb_price_touch_' + self.ticker_name)
        self.line_edit_message = getattr(self.scanner_ui, 'le_msg_' + self.ticker_name)
        self.line_edit_fixed_price = getattr(self.scanner_ui, 'le_price_touch_' + self.ticker_name)
        self.btn_submit = getattr(self.scanner_ui, 'submit_' + self.ticker_name)
        self.btn_cancel = getattr(self.scanner_ui, 'cancel_' + self.ticker_name)

        self.name_widget_dict = {
            'ckb_p5ema8_' + self.ticker_name: self.ckb_p5ema8,
            'ckb_p5ema21_' + self.ticker_name: self.ckb_p5ema21,
            'ckb_p5ema50_' + self.ticker_name: self.ckb_p5ema50,
            'ckb_p15ema8_' + self.ticker_name: self.ckb_p15ema8,
            'ckb_p15ema21_' + self.ticker_name: self.ckb_p15ema21,
            'ckb_p15ema50_' + self.ticker_name: self.ckb_p15ema50,
            'ckb_p60ema8_' + self.ticker_name: self.ckb_p60ema8,
            'ckb_p60ema21_' + self.ticker_name: self.ckb_p60ema21,
            # 'ckb_p240ema8_' + self.ticker_name: self.ckb_p240ema8,
            'ckb_price_touch_' + self.ticker_name: self.ckb_price_touch,
            'le_msg_' + self.ticker_name: self.line_edit_message,
            'le_price_touch_' + self.ticker_name: self.line_edit_fixed_price,
            'submit_' + self.ticker_name: self.btn_submit,
            'cancel_' + self.ticker_name: self.btn_cancel,
        }

        self.widget_name_dict = {
            self.ckb_p5ema8: 'ckb_p5ema8_' + self.ticker_name,
            self.ckb_p5ema21: 'ckb_p5ema21_' + self.ticker_name,
            self.ckb_p5ema50: 'ckb_p5ema50_' + self.ticker_name,
            self.ckb_p15ema8: 'ckb_p15ema8_' + self.ticker_name,
            self.ckb_p15ema21: 'ckb_p15ema21_' + self.ticker_name,
            self.ckb_p15ema50: 'ckb_p15ema50_' + self.ticker_name,
            self.ckb_p60ema8: 'ckb_p60ema8_' + self.ticker_name,
            self.ckb_p60ema21: 'ckb_p60ema21_' + self.ticker_name,
            # self.ckb_p240ema8: 'ckb_p240ema8_' + self.ticker_name,
            self.ckb_price_touch: 'ckb_price_touch_' + self.ticker_name,
            self.line_edit_message: 'le_msg_' + self.ticker_name,
            self.line_edit_fixed_price: 'le_price_touch_' + self.ticker_name,
            self.btn_submit: 'submit_' + self.ticker_name,
            self.btn_cancel: 'cancel_' + self.ticker_name,
        }

        self.widget_watcher_dict = {
            self.ckb_p5ema8: Watchers.P5EMA8,
            self.ckb_p5ema21: Watchers.P5EMA21,
            self.ckb_p5ema50: Watchers.P5EMA50,
            self.ckb_p15ema8: Watchers.P15EMA8,
            self.ckb_p15ema21: Watchers.P15EMA21,
            self.ckb_p15ema50: Watchers.P15EMA50,
            self.ckb_p60ema8: Watchers.P60EMA8,
            self.ckb_p60ema21: Watchers.P60EMA21,
            # self.ckb_p240ema8: Watchers.P240EMA8,
            self.ckb_price_touch: Watchers.PRICE_TOUCHE
        }
        self.watcher_widget_dict = {
            Watchers.P5EMA8: self.ckb_p5ema8,
            Watchers.P5EMA21: self.ckb_p5ema21,
            Watchers.P5EMA50: self.ckb_p5ema50,
            Watchers.P15EMA8: self.ckb_p15ema8,
            Watchers.P15EMA21: self.ckb_p15ema21,
            Watchers.P15EMA50: self.ckb_p15ema50,
            Watchers.P60EMA8: self.ckb_p60ema8,
            Watchers.P60EMA21: self.ckb_p60ema21,
            # Watchers.P240EMA8: self.ckb_p240ema8,
            Watchers.PRICE_TOUCHE: self.ckb_price_touch
        }

        self.btn_submit.clicked.connect(self.btn_submit_callback)
        self.btn_cancel.clicked.connect(self.btn_cancel_callback)

    def btn_submit_callback(self):
        watchers = []
        for checkbox, watcher in self.widget_watcher_dict.items():
            if checkbox.isChecked() and checkbox.isEnabled():
                widget_name = self.widget_name_dict[checkbox]
                self.scanner_ui.set_widget_enabled(widget_name, False)
                self.scanner_ui.set_widget_bg_color(widget_name, "red")
                watchers.append(watcher)

        message = self.line_edit_message.text()
        fixed_price = float(self.line_edit_fixed_price.text()) if self.ckb_price_touch.isChecked() else None
        self.scanner_ui.set_widget_text(self.widget_name_dict[self.line_edit_message], "")
        self.scanner_ui.submit_callback(self.ticker_name, watchers, message, fixed_price)

    def btn_cancel_callback(self):
        for checkbox in self.widget_watcher_dict.keys():
            widget_name = self.widget_name_dict[checkbox]
            self.scanner_ui.set_checkbox_checked(widget_name, False)
            self.scanner_ui.set_widget_enabled(widget_name, True)
            self.scanner_ui.set_widget_bg_color(widget_name, "none")
        self.scanner_ui.cancel_callback(self.ticker_name)

    def get_get_widget_name(self, watcher: Watchers) -> str:
        widget = self.watcher_widget_dict[watcher]
        return self.widget_name_dict[widget]
