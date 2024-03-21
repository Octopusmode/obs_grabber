# Скрипт для конвертирования разметки в формат YOLO
from pathlib import Path
import shutil
from tqdm import tqdm

src_dir = Path('d:/frames')
old_dir = Path('d:/frames/old')

old_dir.mkdir(parents=True, exist_ok=True)

for src_file in tqdm(src_dir.glob('*.txt'), desc='Converting'):
    with src_file.open('r') as file:  # Указываем кодировку
        lines = file.readlines()
        
    if len(lines[0].strip().split()) > 5: # Если разметка ещё не в формате YOLO
        # Создаём копию файла со старой разметкой в папке old
        shutil.copy(src_file, old_dir)
        # Создаём новый файл с разметкой в формате YOLO
        with src_file.open('w') as file:
            for line in lines:
                x1, y1, x2, y2, id, conf = map(float, line.strip().split())
                x = (x1 + x2) / 2
                y = (y1 + y2) / 2
                w = x2 - x1
                h = y2 - y1
                file.write(f'{int(id)} {x} {y} {w} {h}\n')
    else:
        print(f'File {src_file} is already in YOLO format')