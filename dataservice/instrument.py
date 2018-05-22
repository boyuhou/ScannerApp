import time

import numpy as np
import pandas as pd

import pyiqfeed as iq
from pyiqfeed import SilentBarListener


class Instrument(SilentBarListener):

    """
    Instrument is a base class for other indicator classes

    It makes call to pyiqfeed service and update data frame
    """

    INTERVAL_TYPE = "s"
    DATE_COLUMN = "date"
    TIME_COLUMN = "time"

    def __init__(self, ticker: str, interval_in_seconds: int, bars_to_load: int, avg_period: int):
        SilentBarListener.__init__(self, name="{} listener".format(ticker))
        self.ticker = ticker
        self.bars_interval = interval_in_seconds
        self.bars_to_load = bars_to_load
        self.avg_period = avg_period
        self.df = pd.DataFrame()
        self.is_sorted = False
        self._start_listening()

    def _start_listening(self):
        conn = iq.BarConn(name="{} - live, {} minutes interval".format(self.ticker, self.bars_interval))
        conn.add_listener(self)
        with iq.ConnConnector([conn]) as connector:
            conn.watch(symbol=self.ticker,
                       interval_len=self.bars_interval,
                       interval_type=Instrument.INTERVAL_TYPE,
                       update=self.bars_interval,
                       lookback_bars=self.bars_to_load)
            while True:
                time.sleep(30000)

    def on_data(self):
        self.df['avg'] = self.df['close_p'].rolling(window=self.avg_period).mean()
        print("{} - {} bars moving average: {}".format(self.ticker, self.avg_period, self.df['avg'].iloc[-1]))

    """
    Listener
    """

    def process_history_bar(self, bar_data: np.array) -> None:
        self.df = self.df.append(pd.DataFrame(bar_data))

    def process_live_bar(self, bar_data: np.array) -> None:
        """
        Inserts the most recent data record and removes the oldest one, and calls on_data
        :param bar_data:
        :return:
        """
        record = pd.DataFrame(bar_data)
        if not self.is_sorted:
            self.df = self._remove_possible_duplicates(record)
            self.df = self.df.sort_values(by=[Instrument.DATE_COLUMN, Instrument.TIME_COLUMN])
            self.is_sorted = True
        self.df = self.df.append(record)
        self.df = self.df[1:]
        self.on_data()

    def _remove_possible_duplicates(self, possible_duplicate_record: pd.DataFrame) -> pd.DataFrame:
        """
        Removes possible duplicates (the last historical data record and first live data record)
        :param bar_data:
        :return:
        """
        date_value = possible_duplicate_record[Instrument.DATE_COLUMN][0]
        time_value = possible_duplicate_record[Instrument.TIME_COLUMN][0]
        df = self.df[~((self.df[Instrument.DATE_COLUMN] == date_value) & self.df[Instrument.TIME_COLUMN] == time_value)]
        return df

    """
    Thread
    """
    def run(self):
        while True:
            pass

