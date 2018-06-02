import pyiqfeed as iq
from dataservice.listeners import QuoteListener
import cherrypy

ticker = 'USDCAD.FXCM'


bar_conn = iq.BarConn(name='test live interval bars')
bar_listener = QuoteListener('customized bar listener')
bar_conn.add_listener(bar_listener)


class Root(object):
    @cherrypy.expose
    def index(self):
        return "Hello World!"


if __name__ == '__main__':
    with iq.ConnConnector([bar_conn]) as conn:
        # bar_conn.watch(symbol=ticker, interval_len=60 * 60 , interval_type='s', update=10, lookback_bars=400)
        # bar_conn.watch(symbol='EURUSD.FXCM', interval_len=1 * 60, interval_type='s', update=1, lookback_bars=400)
        bar_conn.watch(symbol='EURUSD.FXCM', interval_len=5 * 60, interval_type='s', update=1, lookback_bars=400)
        # bar_conn.watch(symbol='EURUSD.FXCM', interval_len=15 * 60, interval_type='s', update=1, lookback_bars=400)
        # bar_conn.watch(symbol='EURUSD.FXCM', interval_len=60 * 60, interval_type='s', update=1, lookback_bars=400)
        cherrypy.quickstart(Root(), '/')

