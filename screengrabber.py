import cv2
import mss
import numpy as np
import time
from ultralytics import YOLO

class ScreenCapture:
    def __init__(self, monitor_number=2):
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

cycle_time = 120
cur_time = time.time()
last_time = cur_time

if __name__ == "__main__":
    cap = ScreenCapture()
    while True:
        img = cap.capture()
        cv2.imshow("Screen", img)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
        if key == ord("s"):
            cv2.imwrite(f"x:/trucks_raw/screenshot_{cur_time}.png", img)
            print("Screenshot manualy saved!")
            
        cur_time = time.time()    
            
        if cur_time - last_time > cycle_time:
            last_time = time.time()
            cv2.imwrite(f"x:/trucks_raw/every_{cycle_time}_{cur_time}.png", img)
            print(f"Screenshot saved {time.time()}")
            
        cv2.setWindowTitle("Screen", f"{cur_time=:0.2f} {last_time=:0.2f} {cur_time - last_time=:0.2f} {cycle_time=:0.2f}")
        
        
    cv2.destroyAllWindows()