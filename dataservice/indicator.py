import collections


class Ticker:
    def __init__(self):
        self.current_time = None
        self.current_price = None

        self.min_01_high = None
        self.min_01_low = None

        self.min_05_ema_08 = None
        self.min_05_ema_21 = None
        self.min_05_ema_50 = None

        self.min_15_ema_08 = None
        self.min_15_ema_21 = None
        self.min_15_ema_50 = None

        self.min_60_ema_08 = None
        self.min_60_ema_21 = None
        self.min_60_ema_50 = None

        self.min_240_ema_08 = None
        self.min_240_ema_21 = None
        self.min_240_ema_50 = None

        self.min_05_list = collections.deque(maxlen=50)
        self.min_15_list = collections.deque(maxlen=50)
        self.min_60_list = collections.deque(maxlen=50)
        self.min_240_list = collections.deque(maxlen=50)

        self.datetime_05_list = collections.deque(maxlen=50)
        self.datetime_15_list = collections.deque(maxlen=50)
        self.datetime_60_list = collections.deque(maxlen=50)
        self.datetime_240_list = collections.deque(maxlen=50)
