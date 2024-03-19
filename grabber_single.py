import logging
import cv2
from multiprocessing import Process, Queue
from urllib.parse import urlparse
from time import sleep
import numpy as np
from collections import deque
from time import time

from ultralytics import YOLO

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

model = YOLO('yolov8l.pt', verbose=False)
model.to('cuda')

TARGET_CLASSES = [7]
CONF = 0.5

if __name__ == '__main__':
    data_file = 'data/rtsp_links.txt'
    links = []
    with open(data_file, 'r') as file:
        links = [link.strip() for link in file.readlines()]
    links = list(set(links)) #[:3]
    links_count = len(links)
    logging.debug(f'Found {links_count} unique links')

    caps = []
    broken_links = []
    
    for link in links:
        cap = cv2.VideoCapture(link)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 3)

        if not cap.isOpened():
            logging.error(f'Cannot open {link}')
            broken_links.append(link)
            continue
        caps.append((cap, link))
        
    logging.debug(f'Found {len(caps)} working links')
    
    frame_index = 0
    
    while len(caps):
        cycle_start = time()
        for cap, link in caps:
            # очищаем буфер
            for _ in range(5):
                ret, frame = cap.read()
                if not ret:
                    logging.error(f'Cannot read frame from {link}')
                    caps.remove((cap, link))
                    broken_links.append(link)
                    continue
                if frame is None:
                    logging.error(f'Empty frame from {link}')
                    continue
        
            # frame = cv2.imread('example.png')
              
            predictions = model(frame)
            
            objects = []
            
            for prediction in predictions:
                boxes = prediction.boxes.xyxy.cpu().numpy()
                classes = prediction.boxes.cls.cpu().numpy()
                confs = prediction.boxes.conf.cpu().numpy()
                
                # Проверить, что в confs есть TARGET_CLASSES
                # Вернуть список индексов, где есть TARGET_CLASSES
                target_classes = [i for i, cls in enumerate(classes) if cls in TARGET_CLASSES and confs[i] > CONF]
                
                if len(target_classes) == 0:
                    continue
                # Сохранить информацию о найденных объектах в список
                # В формате x1, y1, x2, y2, class, conf
                for i in target_classes:
                    x1, y1, x2, y2 = boxes[i]
                    object_height = y2 - y1
                    conf = confs[i]
                    objects.append((x1, y1, x2, y2, classes[i], conf))
                    
            if len(objects) > 0:
                logging.debug(f'Found {len(objects)} objects in {link}')
                timestamp = time()
                cv2.imwrite(f'x:/frames/frame_{timestamp}.jpg', frame)
                with open(f'x:/frames/frame_{timestamp}.txt', 'w') as file:
                    for obj in objects:
                        file.write(f'{obj[0]} {obj[1]} {obj[2]} {obj[3]} {obj[4]} {obj[5]}\n')
                # for obj in objects:
                #     logging.debug(f'Object: {obj}')
        
        print(f'Cycle time: {time() - cycle_start}')