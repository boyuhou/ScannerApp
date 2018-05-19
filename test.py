import pyiqfeed as iq

ticker = 'USDCAD.FXCM'


bar_conn = iq.BarConn(name='test live interval bars')
bar_listener = iq.VerboseBarListener('bar listener')
bar_conn.add_listener(bar_listener)

with iq.ConnConnector([bar_conn]) as conn:
    bar_conn.watch(symbol=ticker, interval_len=60, interval_type='s', update=1, lookback_bars=10)