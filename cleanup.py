import os
import cv2
import shutil
from skimage.metrics import structural_similarity as ssim
from tqdm import tqdm
from collections import defaultdict
from multiprocessing import Pool

def compare_images(imageA, imageB):
    if imageA is None or imageB is None:
        return 0
    return ssim(imageA, imageB)

image_dir = "x:/frames"
move_dir = "x:/frames/similar"
threshold = 0.9

print("Loading images...")
image_files = [f for f in os.listdir(image_dir) if f.endswith(".png")] # [:300]

# Group files by source name
source_files = defaultdict(list)
source_images = {}
for f in tqdm(image_files):
    source_name = f.split('_')[1]
    source_files[source_name].append(f)
    image = cv2.imread(os.path.join(image_dir, f))
    if image is None:
        print(f"Failed to load {f}")
        # удалить файл, который не удалось загрузить .png и .txt
        # вернуть имя файла без расширения
        file_name = os.path.splitext(f)[0]
        # удалить файл .png
        os.remove(os.path.join(image_dir, file_name + '.png'))
        # удалить файл .txt
        os.remove(os.path.join(image_dir, file_name + '.txt'))
        
        continue
    image = cv2.resize(image, (320, 320))
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    source_images[f] = image

print(f"Loaded {len(image_files)} images from {len(source_files)} sources")

def process_source(args):
    source_name, files = args
    to_move = set()
    to_compare = list(files)  # Copy the list of files
    for i, nameA in enumerate(tqdm(to_compare, desc=f"Comparing images from source {source_name}")):
        imageA = source_images[nameA]
        # print(f"Comparing with {nameA}")
        for nameB in tqdm(to_compare[i+1:], desc=f"Comparing with {nameA}", leave=False):
            imageB = source_images[nameB]
            if compare_images(imageA, imageB) > threshold:
                # print(f"Found similar images: {nameA} and {nameB}")
                to_move.add(nameB)
                to_compare.remove(nameB)  # Remove the image from the list of images to compare
    print(f"Found {len(to_move)} similar images in source {source_name}")
    for name in to_move:
        shutil.move(os.path.join(image_dir, name), os.path.join(move_dir, name))
        txt_name = os.path.splitext(name)[0] + '.txt'
        txt_path = os.path.join(image_dir, txt_name)
        if os.path.exists(txt_path):
            shutil.move(txt_path, os.path.join(move_dir, txt_name))

if __name__ == "__main__":
    with Pool(16) as p:
        p.map(process_source, source_files.items())