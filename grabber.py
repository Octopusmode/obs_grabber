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
from urllib.parse import urlparse
from time import sleep

logging.basicConfig(level=logging.DEBUG)


def is_url(s):
    try:
        result = urlparse(s)
        return all((result.scheme, result.netloc))
    except ValueError:
        return False
    
class VideoReader(Process):
    def __init__(self, link, frame_queue):
        super().__init__()
        self.is_valid = is_url(link)
        self.link = link
        self.frame_queue = frame_queue
        self.cap = None
        logging.debug(f'{self.name} created with link {link}')
        
    def run(self):
        while True:
            if not self.is_cap_open():
                self.cap = cv2.VideoCapture(self.link)
                logging.debug(f'{self.name} opened {self.link}')
                sleep(1)
            ret, frame = self.cap.read()
            if not ret:
                self.cap.release()
                self.cap = None
                logging.debug(f'{self.name} closed {self.link}')
                sleep(1)
                continue
            # preprocessing here
            logging.debug(f'{self.name} put frame from {self.link} to queue')
            self.frame_queue.put((self.name, frame))
            
    def stop(self):
        if self.is_cap_open():
            self.cap.release()
            logging.debug(f'{self.name} terminated {self.link}')
        self.terminate()
        
    def is_cap_open(self):
        return self.cap is not None and self.cap.isOpened()
    
    
    # Читаем уникальные ссылки из файла
data_file = 'data/rtsp_links.txt'
links = []
with open(data_file, 'r') as file:
    links = file.readlines()[:4]
links = list(set(links))
print(f'Found {len(links)} unique links')


if __name__ == '__main__':
    # Создаем очередь для фреймов
    frame_queue = Queue()

    # Создаем и запускаем процессы VideoReader
    video_links = ['link1', 'link2', 'link3']
    readers = [VideoReader(link, frame_queue) for link in video_links]
    for reader in readers:
        reader.start()

    # Извлекаем фреймы из очереди
    frames = []
    while True:
        if not frame_queue.empty():
            frames.append(frame_queue.get())
        else:
            break

    # Останавливаем процессы VideoReader
    for reader in readers:
        reader.stop()
    