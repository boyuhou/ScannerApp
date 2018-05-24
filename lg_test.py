from dataservice import Instrument
import threading
import time


if __name__ == "__main__":

    instrument = Instrument(ticker='AUDUSD.FXCM', interval_in_seconds=60, bars_to_load=100, avg_period=21)

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



