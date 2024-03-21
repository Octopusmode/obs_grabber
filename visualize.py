# Скрипт для отрисовки аннотаций формата YOLO
from pathlib import Path
import cv2
import shutil

def draw_annotation(image_path, annotation_path):
    image = cv2.imread(str(image_path))
    with annotation_path.open('r') as file:
        for line in file:
            height, width, _ = image.shape
            id, x, y, w, h = map(float, line.strip().split())
            # Нормализованные координаты в пиксельные
            x = x * width
            y = y * height
            w = w * width
            h = h * height
            x1 = int(x - w / 2)
            y1 = int(y - h / 2)
            x2 = int(x + w / 2)
            y2 = int(y + h / 2)
            # Отобразить имя файла
            print(f'File {annotation_path}')
            # Отобразить объект
            print(f'Object {id} at ({x1}, {y1})-({x2}, {y2})')
            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
    return image

if __name__ == "__main__":
    # Получить имена файлов из папки без расширения
    image_dir = Path('x:/test')
    annotation_dir = Path('x:/test')
    trash_dir = Path('x:/test/trash')
    not_sure_dir = Path('x:/test/not_sure')

    trash_dir.mkdir(parents=True, exist_ok=True)
    not_sure_dir.mkdir(parents=True, exist_ok=True)
    
    image_files = [f for f in image_dir.glob('*.png')]
    annotation_files = [f for f in annotation_dir.glob('*.txt')]
    for image_path in image_files:
        annotation_path = annotation_dir / (image_path.stem + '.txt')
        if annotation_path in annotation_files:
            image = draw_annotation(image_path, annotation_path)
            cv2.imshow('Render', image)
            key = cv2.waitKey(0) & 0xFF
            if key == ord('q'):
                break
            if key == ord('d'):
                # Переместить файлы с изображением и аннотациями в папку trash
                shutil.move(image_path, trash_dir)
                shutil.move(annotation_path, trash_dir)
                print(f'{image_path} with annotations is moved to trash')
            if key == ord('n'):
                shutil.move(image_path, not_sure_dir)
                shutil.move(annotation_path, not_sure_dir)
                print(f'{image_path} with annotations is moved to not_sure')
        else:
            print(f'Annotation file for {image_path} not found')
cv2.destroyAllWindows()