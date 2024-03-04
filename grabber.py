"""
    Скрипт читает ссылки на rtsp-потоки из файла
    Создаёт список уникальных ссылок
    Создаёт экземпляр cv2.VideoCapture для каждой ссылки
    Создаёт батч из всех фреймов полученных из всех потоков
    Отправляет батч в модель
    Сохраняет все фреймы где есть файлы с нужными классами в отдельную папку
    Вместе с фреймами сохраняются боундинг боксы и классы обнаруженных объектов
"""
import logging
import cv2
from multiprocessing import Process, Queue
import requests
from urllib.parse import urlparse
from time import sleep
import numpy as np
import math
from collections import deque

logging.basicConfig(level=logging.DEBUG)


# def is_url(s):
#     try:
#         result = urlparse(s)
#         if all([result.scheme, result.netloc]):
#             response = requests.get(s, timeout=5)
#             return response.status_code == 200
#         else:
#             return False
#     except (requests.ConnectionError, requests.Timeout, ValueError):
#         return False

def is_url(s):
    return True

def create_mosaic(frames, final_size=(1000, 1000)):
    start = cv2.getTickCount()
    _frames = frames.copy()
    # Посчитать общее количество изображений
    n_frames = len(_frames)
    # Посчитать сколько получается столбцов и строк
    aspect_ratio = final_size[0] / final_size[1]
    n_cols = round(math.sqrt(n_frames * aspect_ratio))
    n_rows = n_frames // n_cols

    # Обрезать каждое изображение под пропорции размера мозаики
    frame_size = (final_size[0] // n_cols, final_size[1] // n_rows)

    # Если количество элементов не чётное, то добавить черный элемент
    if n_frames % n_cols != 0:
        black_frame = np.zeros((frame_size[1], frame_size[0], 3), dtype=np.uint8)
        _frames.append(black_frame)
        n_frames += 1
        n_rows = n_frames // n_cols
    # Обрезать каждое изображение под пропорции размера мозаики
    frame_size = (final_size[0] // n_cols, final_size[1] // n_rows)
    resized_frames = []
    
    for frame in _frames:

        height, width = frame.shape[:2]
        new_width = min(frame_size[0], width)
        new_height = min(frame_size[1], height)
        left = (width - new_width) // 2
        top = (height - new_height) // 2
        right = (width + new_width) // 2
        bottom = (height + new_height) // 2
        frame = frame[top:bottom, left:right]
        resized_frames.append(frame)
    # Ресайзнуть каждое изображение до размера элемента мозаики
    resized_frames = [cv2.resize(frame, frame_size, interpolation=cv2.INTER_NEAREST) for frame in resized_frames]
    # Если изображений не хватает, добавляем черные изображения
    while len(resized_frames) < n_rows * n_cols:
        black_frame = np.zeros((frame_size[1], frame_size[0], 3), dtype=np.uint8)
        resized_frames.append(black_frame)
    # Собрать все получившиеся изображения в мозаику
    mosaic = []
    for i in range(n_rows):
        row = np.hstack(resized_frames[i*n_cols:(i+1)*n_cols])
        mosaic.append(row)
    mosaic = np.vstack(mosaic)
    logging.debug(f'Mosaic created in {(cv2.getTickCount() - start) / cv2.getTickFrequency()} seconds')
    return mosaic
    
    
class VideoReader(Process):
    def __init__(self, link, frame_queue):
        super().__init__()
        self.is_valid = is_url(link)
        self.link = link
        self.frame_queue = frame_queue
        self.cap = None
        self.is_stopped = False
        # logging.debug(f'{self.name} created with link {link}')
        
    def run(self):
        while not self.is_stopped:
            if self.cap is None:
                self.start_capture()
            ret, frame = self.cap.read()
            if not ret:
                self.cap.release()
                self.cap = None
                logging.debug(f'{self.name} closed {self.link}')
                self.start_capture()
            # preprocessing here
            logging.debug(f'{self.name} put frame from {self.link} to queue')
            sleep(1)
            self.frame_queue.put((self.name, frame))
        
    def start_capture(self):
        if self.is_valid:
            self.cap = cv2.VideoCapture(self.link)
            # logging.debug(f'{self.name} started {self.link}')
        else:
            logging.debug(f'{self.name} is not valid {self.link}')
            
    def stop(self):
        self.is_stopped = True
        if self.cap.is_cap_open():
            self.cap.release()
            # logging.debug(f'{self.name} terminated {self.link}')
        self.terminate()
        
    def is_cap_open(self):
        return self.cap is not None and self.cap.isOpened()
    
    
data_file = 'data/rtsp_links.txt'
links = []
with open(data_file, 'r') as file:
    links = [link.strip() for link in file.readlines()]
links = list(set(links[:10]))
print(f'Found {len(links)} unique links')


if __name__ == '__main__':
    frame_queue = Queue()
    readers = [VideoReader(link, frame_queue) for link in links]
    for reader in readers:
        reader.start()
    
    running = True  # Флаг для контроля состояния программы
    
    frames = deque(maxlen=80)
    
    while running:
        while not frame_queue.empty():
            name, frame = frame_queue.get()
            frames.append((name, frame))
        print(f'Got {len(frames)} frames')
        sleep(1)
        if len(frames) > 0:
            mosaic = create_mosaic([frame for name, frame in frames])
            cv2.imshow('Mosaic', mosaic)
        if cv2.waitKey(1) & 0xFF == ord('q'):
              # Установка флага в False для остановки программы
            for reader in readers:
                reader.stop()
        # Проверить, что все потоки is_stopped
        if all([reader.is_stopped for reader in readers]):
            # Если все потоки остановлены, то завершить программу
            running = False
        
    cv2.destroyAllWindows()