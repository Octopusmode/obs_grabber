import cv2
import mss
import numpy as np
import time
import keyboard
import winsound
import os

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

save_dir = "d:/trucks_raw"

def save_frame():
    winsound.PlaySound("SystemExit", winsound.SND_ALIAS)
    cv2.imwrite(f"{save_dir}/screenshot_{cur_time}.png", img)
    print("Screenshot manualy saved!")
    
os.makedirs(f"{save_dir}", exist_ok=True)  
    
keyboard.add_hotkey('ctrl+shift+plus', save_frame, args=(''))

cv2.namedWindow('Screen', cv2.WINDOW_AUTOSIZE)

if __name__ == "__main__":
    cap = ScreenCapture()
    while True:
        img = cap.capture()
        render = cv2.resize(img, (270, 120))
        cv2.imshow("Screen", render)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("s"):
            save_frame()
        
        if key == ord("q"):
            break
        # if key == ord("s"):
        #     save_frame()
            
        cur_time = time.time()    
            
        if cur_time - last_time > cycle_time:
            last_time = time.time()
            cv2.imwrite(f"{save_dir}/every_{cycle_time}_{cur_time}.png", img)
            print(f"Screenshot saved {time.time()}")
            
        cv2.setWindowTitle("Screen", f"{cur_time=:0.2f} {last_time=:0.2f} {cur_time - last_time=:0.2f} {cycle_time=:0.2f}")
        
    cv2.destroyAllWindows()