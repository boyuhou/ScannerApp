import pyiqfeed as iq
from dataservice.listeners import QuoteListener
import time

ticker = 'USDCAD.FXCM'


bar_conn = iq.BarConn(name='test live interval bars')
bar_listener = QuoteListener('customized bar listener')
bar_conn.add_listener(bar_listener)

with iq.ConnConnector([bar_conn]) as conn:
    bar_conn.watch(symbol=ticker, interval_len=60 * 60 , interval_type='s', update=10, lookback_bars=10)
    bar_conn.watch(symbol='AUDCAD.FXCM', interval_len=5 * 60, interval_type='s', update=1, lookback_bars=5)
    time.sleep(5000)
