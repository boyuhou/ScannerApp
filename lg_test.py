import sys

from PyQt5 import QtWidgets

import pyiqfeed as iq
from dataservice.listener import QuoteListener
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

if __name__ == "__main__":
    """
    Init GUI
    """
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)

    """
    Init listener
    """
    bar_conn = iq.BarConn(name='scanner app connection')
    bar_listener = QuoteListener(name='customized bar listener', ui=ui, tickers=tickers, is_debug=True)
    bar_conn.add_listener(bar_listener)

    with iq.ConnConnector([bar_conn]) as conn:
        # for ticker in tickers:
        #     bar_conn.watch(symbol=ticker, interval_len=1 * 60, interval_type='s', update=1, lookback_bars=205)
        #     bar_conn.watch(symbol=ticker, interval_len=5 * 60, interval_type='s', update=1, lookback_bars=205)
        #     bar_conn.watch(symbol=ticker, interval_len=15 * 60, interval_type='s', update=1, lookback_bars=205)
        #     bar_conn.watch(symbol=ticker, interval_len=60 * 60, interval_type='s', update=1, lookback_bars=205)

        Dialog.show()
        sys.exit(app.exec_())
