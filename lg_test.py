import sys
import time

import numpy as np
from PyQt5 import QtWidgets

import pyiqfeed as iq
from dataservice.listeners import QuoteListener
from ui.test import Ui_Dialog

tickers = ['AUDCAD.FXCM',
           'AUDCHF.FXCM',
           'AUDJPY.FXCM',
           'AUDNZD.FXCM',
           'AUDUSD.FXCM',
           'CADCHF.FXCM',
           'CADJPY.FXCM',
           'CHFJPY.FXCM',
           'EURAUD.FXCM',
           'EURCAD.FXCM',
           'EURCHF.FXCM',
           'EURGBP.FXCM',
           'EURJPY.FXCM',
           'EURNZD.FXCM',
           'EURUSD.FXCM',
           'GBPAUD.FXCM',
           'GBPCAD.FXCM',
           'GBPCHF.FXCM',
           'GBPJPY.FXCM',
           'GBPNZD.FXCM',
           'GBPUSD.FXCM',
           'NZDCAD.FXCM',
           'NZDCHF.FXCM',
           'NZDJPY.FXCM',
           'NZDUSD.FXCM',
           'USDCAD.FXCM',
           'USDCHF.FXCM',
           'USDJPY.FXCM',
           ]


def callback(bar_data: np.array):
    print(bar_data['datetime'][0])
    full_name = bar_data['symbol'][0]
    label_name = full_name.split('.')[0] + '_PRICE'
    text_field = getattr(ui, label_name)
    text_field.setText(str(bar_data['close_p'][0]))


if __name__ == "__main__":

    # init listener
    bar_conn = iq.BarConn(name='test live interval bars')
    bar_listener = QuoteListener('customized bar listener', callback)
    bar_conn.add_listener(bar_listener)
    with iq.ConnConnector([bar_conn]) as conn:
        for ticker in tickers:
            print('watching {}'.format(ticker))
            bar_conn.watch(symbol=ticker, interval_len=1 * 60, interval_type='s', update=1, lookback_bars=205)
            bar_conn.watch(symbol=ticker, interval_len=5 * 60, interval_type='s', update=1, lookback_bars=205)
            bar_conn.watch(symbol=ticker, interval_len=15 * 60, interval_type='s', update=1, lookback_bars=205)
            bar_conn.watch(symbol=ticker, interval_len=60 * 60, interval_type='s', update=1, lookback_bars=205)

        # init gui
        app = QtWidgets.QApplication(sys.argv)
        Dialog = QtWidgets.QDialog()
        ui = Ui_Dialog()
        ui.setupUi(Dialog)
        Dialog.show()
        sys.exit(app.exec_())


