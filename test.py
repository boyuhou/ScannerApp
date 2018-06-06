import pyiqfeed as iq
from dataservice.listener import QuoteListener
import cherrypy

ticker = 'USDCAD.FXCM'


def callback(bar_data):
    pass


bar_conn = iq.BarConn(name='test live interval bars')
bar_listener = QuoteListener('customized bar listener', callback)
bar_conn.add_listener(bar_listener)


class Root(object):
    @cherrypy.expose
    def index(self):
        return "Hello World!"


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


if __name__ == '__main__':
    with iq.ConnConnector([bar_conn]) as conn:
        for ticker in tickers:
            bar_conn.watch(symbol=ticker, interval_len=1 * 60, interval_type='s', update=1, lookback_bars=205)
            bar_conn.watch(symbol=ticker, interval_len=5 * 60, interval_type='s', update=1, lookback_bars=205)
            bar_conn.watch(symbol=ticker, interval_len=15 * 60, interval_type='s', update=1, lookback_bars=205)
            bar_conn.watch(symbol=ticker, interval_len=60 * 60, interval_type='s', update=1, lookback_bars=205)

        # bar_conn.watch(symbol=ticker, interval_len=60 * 60 , interval_type='s', update=10, lookback_bars=400)
        # bar_conn.watch(symbol='EURUSD.FXCM', interval_len=1 * 60, interval_type='s', update=1, lookback_bars=400)
        # bar_conn.watch(symbol='EURUSD.FXCM', interval_len=5 * 60, interval_type='s', update=1, lookback_bars=400)
        # bar_conn.watch(symbol='EURUSD.FXCM', interval_len=15 * 60, interval_type='s', update=1, lookback_bars=400)
        # bar_conn.watch(symbol='EURUSD.FXCM', interval_len=60 * 60, interval_type='s', update=1, lookback_bars=400)
        # bar_conn.watch(symbol='AUDUSD.FXCM', interval_len=1 * 60, interval_type='s', update=1, lookback_bars=400)
        # bar_conn.watch(symbol='AUDUSD.FXCM', interval_len=5 * 60, interval_type='s', update=1, lookback_bars=400)
        # bar_conn.watch(symbol='AUDUSD.FXCM', interval_len=15 * 60, interval_type='s', update=1, lookback_bars=400)
        # bar_conn.watch(symbol='AUDUSD.FXCM', interval_len=60 * 60, interval_type='s', update=1, lookback_bars=400)
        cherrypy.quickstart(Root(), '/')

