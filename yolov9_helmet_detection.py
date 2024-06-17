# -*- coding: utf-8 -*-
"""YOLOv9_Helmet detection.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1nKMCrUOD5lHDahFgtGQRyl1Zxk5ZnhEO

#Precheck
"""

from google.colab import drive
drive.mount('/content/drive')

# Check GPU
!nvidia-smi

"""# Clone repo github YOLOv9"""

# Commented out IPython magic to ensure Python compatibility.
# %cd /content/drive/MyDrive/Helmet_Dectection_YOLOv9

!git clone https://github.com/WongKinYiu/yolov9

# Commented out IPython magic to ensure Python compatibility.
# install requirements

# %cd /content/drive/MyDrive/Helmet_Dectection_YOLOv9/yolov9
!pip install -r requirements.txt

"""# Prepare Data"""

# Commented out IPython magic to ensure Python compatibility.
# %cd /content/drive/MyDrive/Helmet_Dectection_YOLOv9/Dataset

# Create File dataset in GG drive
!mkdir -p Dataset/labels
!mkdir -p Dataset/images

#import libraries

import numpy as np
from pathlib import Path
from shutil import copyfile
import os
import xml.etree.ElementTree as ET

# Converting Pascal VOC Format to YOLO Format

classes = ['helmet', 'head', 'person']

def convert_annot(size, box):
  x_min = int(box[0])
  y_min = int(box[1])
  x_max = int(box[2])
  y_max = int(box[3])

  w = x_max - x_min # width
  h = y_max - y_min # height
  x_center = x_min + (w / 2)
  y_center = y_min + (h / 2)

  dw = np.float32(1 / int(size[0]))
  dh = np.float32(1 / int(size[1]))

  # Standart value
  x = x_center * dw
  w = w * dw
  y = y_center * dh
  h = h * dh

  return [x,y,w,h]

# Save lable file (txt)

def save_label_file(file_name, size, img_box):
  save_file_name = '/content/drive/MyDrive/Helmet_Dectection_YOLOv9/Dataset/Dataset/labels/' + file_name + '.txt'

  with open(save_file_name, 'a') as file_path:
    for box in img_box:

      class_number = classes.index(box[0])

      new_bbox = convert_annot(size, box[1:])

      file_path.write(f"{class_number} {new_bbox[0]} {new_bbox[1]} {new_bbox[2]} {new_bbox[3]}\n")

    file_path.flush()
    file_path.close()

def get_xml_data(file_path, img_xml_file):
    img_path = file_path + '/' + img_xml_file + '.xml'

    tree = ET.parse(img_path)
    root = tree.getroot()

    img_name = root.find("filename").text
    img_size = root.find("size")
    img_w = int(img_size.find("width").text)
    img_h = int(img_size.find("height").text)
    img_c = int(img_size.find("depth").text)

    img_box = []
    for box in root.findall("object"):
        cls_name = box.find("name").text
        x_min = int(box.find("bndbox").find("xmin").text)
        y_min = int(box.find("bndbox").find("ymin").text)
        x_max = int(box.find("bndbox").find("xmax").text)
        y_max = int(box.find("bndbox").find("ymax").text)

        img_box.append([cls_name, x_min, y_min, x_max, y_max])

    img_jpg_file_name = img_xml_file + '.jpg'
    save_label_file(img_xml_file, [img_w, img_h], img_box)

from tqdm import tqdm

files = os.listdir('/content/drive/MyDrive/Helmet_Dectection_YOLOv9/Dataset/Dataset/annotations')
for file in tqdm(files, total=len(files)):
    file_xml = file.split(".")
    get_xml_data('/content/drive/MyDrive/Helmet_Dectection_YOLOv9/Dataset/Dataset/annotations', file_xml[0])

files = os.listdir('/content/drive/MyDrive/Helmet_Dectection_YOLOv9/Dataset/Dataset/labels')
print (len(files))

"""
# Split Dataset"""

from sklearn.model_selection import train_test_split
image_list = os.listdir('/content/drive/MyDrive/Helmet_Dectection_YOLOv9/Dataset/Dataset/images')
train_list, test_list = train_test_split(image_list, test_size=0.2, random_state=42)
val_list, test_list = train_test_split(test_list, test_size=0.5, random_state=42)
print('total =', len(image_list))
print('train :', len(train_list))
print('val   :', len(val_list))
print('test  :', len(test_list))

from pathlib import Path
from shutil import copyfile
from tqdm import tqdm

def copy_data(file_list, img_labels_root, imgs_source, mode):
    dataset_root = Path('/content/drive/MyDrive/Helmet_Dectection_YOLOv9/Dataset/')

    # Create directories if they don't exist
    images_path = dataset_root / 'images' / mode
    labels_path = dataset_root / 'labels' / mode
    images_path.mkdir(parents=True, exist_ok=True)
    labels_path.mkdir(parents=True, exist_ok=True)

    # Copying files with progress bar
    for file in tqdm(file_list, desc=f"Copying {mode} data"):
        base_filename = file.replace('.png', '')

        img_src_file = Path(imgs_source) / (base_filename + '.png')
        label_src_file = Path(img_labels_root) / (base_filename + '.txt')

        img_dest_file = images_path / (base_filename + '.png')
        label_dest_file = labels_path / (base_filename + '.txt')

        copyfile(img_src_file, img_dest_file)
        copyfile(label_src_file, label_dest_file)

# Example usage
copy_data(train_list, '/content/drive/MyDrive/Helmet_Dectection_YOLOv9/Dataset/Dataset/labels', '/content/drive/MyDrive/Helmet_Dectection_YOLOv9/Dataset/Dataset/images', "train")
copy_data(val_list,   '/content/drive/MyDrive/Helmet_Dectection_YOLOv9/Dataset/Dataset/labels', '/content/drive/MyDrive/Helmet_Dectection_YOLOv9/Dataset/Dataset/images', "val")
copy_data(test_list,  '/content/drive/MyDrive/Helmet_Dectection_YOLOv9/Dataset/Dataset/labels', '/content/drive/MyDrive/Helmet_Dectection_YOLOv9/Dataset/Dataset/images', "test")

import yaml

config = {
    "train" : "/content/drive/MyDrive/Helmet_Dectection_YOLOv9/Dataset/images/train",
    "val" : "/content/drive/MyDrive/Helmet_Dectection_YOLOv9/Dataset/images/val",
    "test" : "/content/drive/MyDrive/Helmet_Dectection_YOLOv9/Dataset/images/test",
    "nc" : 3,
    "names" : ['helmet', 'head', 'person']
}

with open("/content/drive/MyDrive/Helmet_Dectection_YOLOv9/Dataset/data.yaml", "w") as file_yml:
  yaml.dump(config, file_yml, default_flow_style = False)

# Commented out IPython magic to ensure Python compatibility.
# %cd /content/drive/MyDrive/Helmet_Dectection_YOLOv9/yolov9/models/detect
!cp /content/drive/MyDrive/Helmet_Dectection_YOLOv9/yolov9/models/detect/yolov9-e.yaml /content/drive/MyDrive/Helmet_Dectection_YOLOv9/yolov9/models/detect/yolov9-e-custom.yaml

"""# Fine tuning model"""

# Commented out IPython magic to ensure Python compatibility.
# train yolov9 models
# %cd /content/drive/MyDrive/Helmet_Dectection_YOLOv9/yolov9
!python train_dual.py --workers 8 --device 0 --batch 4 --data /content/drive/MyDrive/Helmet_Dectection_YOLOv9/Dataset/data.yaml --img 640 --cfg /content/drive/MyDrive/Helmet_Dectection_YOLOv9/yolov9/models/detect/yolov9-e-custom.yaml --weights '/content/drive/MyDrive/Helmet_Dectection_YOLOv9/yolov9/yolov9-e.pt' --name yolov9-c --hyp /content/drive/MyDrive/Helmet_Dectection_YOLOv9/yolov9/data/hyps/hyp.scratch-high.yaml --min-items 0 --epochs 30 --close-mosaic 15

# train gelan models
# python train.py --workers 8 --device 0 --batch 32 --data data/coco.yaml --img 640 --cfg models/detect/gelan-c.yaml --weights '' --name gelan-c --hyp hyp.scratch-high.yaml --min-items 0 --epochs 500 --close-mosaic 15

# Commented out IPython magic to ensure Python compatibility.
# %cd /content/drive/MyDrive/Helmet_Dectection_YOLOv9/yolov9
!python detect.py --weights /content/drive/MyDrive/Helmet_Dectection_YOLOv9/yolov9/runs/train/yolov9-c/weights/best.pt --source /content/drive/MyDrive/Helmet_Dectection_YOLOv9/images.jpeg

from IPython.display import Image
Image(filename = '/content/drive/MyDrive/Helmet_Dectection_YOLOv9/yolov9/runs/detect/exp3/images.jpeg', width = 800)

# Commented out IPython magic to ensure Python compatibility.
# %cd /content/drive/MyDrive/Helmet_Dectection_YOLOv9/yolov9
!python detect.py --weights /content/drive/MyDrive/Helmet_Dectection_YOLOv9/yolov9/runs/train/yolov9-c/weights/best.pt --source /content/drive/MyDrive/Helmet_Dectection_YOLOv9/test.jpeg

from IPython.display import Image
Image(filename = '/content/drive/MyDrive/Helmet_Dectection_YOLOv9/yolov9/runs/detect/exp4/test.jpeg', width = 800)