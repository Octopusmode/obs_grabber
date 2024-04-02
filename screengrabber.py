import mss
import numpy as np

class ScreenCapture:
    def __init__(self, monitor_number=1):
        self.sct = mss.mss()
        self.monitor_number = monitor_number
        self.mon = self.sct.monitors[self.monitor_number]
        self.monitor = {
            "top": self.mon["top"],
            "left": self.mon["left"],
            "width": self.mon["width"],
            "height": self.mon["height"],
            "mon": self.monitor_number,
        }
        self.img = None
        
    def capture(self):
        self.img = np.array(self.sct.grab(self.monitor))
        return self.img