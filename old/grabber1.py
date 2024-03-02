import torch
import cv2
from ultralytics import YOLO
import datetime
from time import sleep

# source_link = 'https://live.cmirit.ru:443/live/ever1_1920x1080.stream/playlist.m3u8'
source_link = 'https://live.cmirit.ru:443/live/arh-most-002.stream/playlist.m3u8'
output_folder = r'./output'

model = YOLO('yolov8l.pt')

print('Is CUDA available: ', torch.cuda.is_available())
print('CUDA version: ', torch.version.cuda)

cap = cv2.VideoCapture(source_link)

k_size = 1.0
r_size = 0.5
# fps = cap.get(cv2.CAP_PROP_FPS)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) * k_size)
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) * k_size)

# total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
# fourcc = cv2.VideoWriter_fourcc(*'H264')  # Be sure to use lower case
# out = cv2.VideoWriter(output_video, fourcc, fps, (width, height))

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    results = model(source=frame)
    
    for result in results:
        boxes = result.boxes
    
    # detection = results.render()[0]
    
    # sleep(1)
    
    # cv2.imwrite('output.png', detection , [cv2.IMWRITE_PNG_COMPRESSION, 9])
    
    cv2.imshow('render', frame)
    if cv2.waitKey(1) == ord('q'):
        break
    
cap.release()
cv2.destroyAllWindows()