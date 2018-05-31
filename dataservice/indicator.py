import collections
import numpy as np


def calc_ewma_vectorized(data, ema, window):
    _size = len(data)
    if _size < window:
        return 0
    elif _size == window:
        return sum(data) / window
    else:
        if isinstance(ema, collections.deque) or isinstance(ema, list):
            previous_ema = ema[-1]
        else:
            previous_ema = ema
        sma_window = sum(data[-8:]) / window
        return (sma_window - previous_ema) * 2 / (window + 1) + previous_ema


class Ticker:
    def __init__(self):
        self.current_time = None
        self.current_price = None

        self.price_high = None
        self.price_low = None

        self.current_ema = {
            5: None,
            15: None,
            60: None,
            240: None
        }

        self.ema_08 = {
            5: collections.deque(maxlen=60),
            15: collections.deque(maxlen=60),
            60: collections.deque(maxlen=60),
            240: collections.deque(maxlen=60),
        }
        self.ema_21 = {
            5: collections.deque(maxlen=60),
            15: collections.deque(maxlen=60),
            60: collections.deque(maxlen=60),
            240: collections.deque(maxlen=60),
        }
        self.ema_50 = {
            5: collections.deque(maxlen=60),
            15: collections.deque(maxlen=60),
            60: collections.deque(maxlen=60),
            240: collections.deque(maxlen=60),
        }

        self.bar_list = {
            5: collections.deque(maxlen=60),
            15: collections.deque(maxlen=60),
            60: collections.deque(maxlen=60),
            240: collections.deque(maxlen=60),
        }

        self.time_list = {
            5: collections.deque(maxlen=50),
            15: collections.deque(maxlen=50),
            60: collections.deque(maxlen=50),
            240: collections.deque(maxlen=50),
        }
