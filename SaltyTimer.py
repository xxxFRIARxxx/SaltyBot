import time

class SaltyTimer:
    def __init__(self):
        self.snapshot = None
        self.timer_start()

    def timer_start(self):
        self.start_time_s = time.perf_counter()

    def timer_snapshot(self):
        self.snapshot = int(round(time.perf_counter() - self.start_time_s, 0))