import time

class FPSCounter:
    def __init__(self):
        self.p_time = 0
        self.fps = 0

    def update(self):
        c_time = time.time()
        if c_time - self.p_time > 0:
            self.fps = 1 / (c_time - self.p_time)
        self.p_time = c_time
        return int(self.fps)
