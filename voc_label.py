# xml解析包
import xml.etree.ElementTree as ET
import pickle
import os
from os import getcwd

# os.listdir() 方法用于返回指定的文件夹包含的文件或文件夹的名字的列表
from os import listdir, getcwd
from os.path import join

sets = ['train', 'test', 'val']
classes = ['Other', 'Kitchen', 'Recycle', 'Harmful']


extension = {}
for xml in os.listdir('data/Annotations'):
    with open(fr'data/Annotations/{xml}', encoding='UTF-8') as fxml:
        tree = ET.parse(fxml)
        root = tree.getroot()
        filename = root.find('filename').text
        f, ex = os.path.splitext(filename)
        extension[f] = ex


def convert(size, box):
    dw = 1. / (size[0])
    dh = 1. / (size[1])
    x = (box[0] + box[1]) / 2.0 - 1
    y = (box[2] + box[3]) / 2.0 - 1
    w = box[1] - box[0]
    h = box[3] - box[2]
    x = x * dw
    w = w * dw
    y = y * dh
    h = h * dh
    return x, y, w, h


def convert_annotation(image_id):
    in_file = open(fr'data/Annotations/{image_id}.xml', encoding='UTF-8')
    out_file = open(fr'data/labels/{image_id}.txt', 'w')
    tree = ET.parse(in_file)
    root = tree.getroot()
    filename = root.find('filename').text
    size = root.find('size')
    w = int(size.find('width').text)
    h = int(size.find('height').text)
    for obj in root.iter('object'):
        difficult = obj.find('difficult').text
        cls = obj.find('name').text
        if cls not in classes or int(difficult) == 1:
            continue
        cls_id = classes.index(cls)
        xmlbox = obj.find('bndbox')
        b = (float(xmlbox.find('xmin').text), float(xmlbox.find('xmax').text), float(xmlbox.find('ymin').text),
            float(xmlbox.find('ymax').text))
        b1, b2, b3, b4 = b
        # 标注越界修正
        if b2 > w:
            b2 = w
        if b4 > h:
            b4 = h
        b = (b1, b2, b3, b4)
        bb = convert((w, h), b)
        out_file.write(str(cls_id) + " " + " ".join([str(a) for a in bb]) + '\n')

    in_file.close()
    out_file.close()


wd = getcwd()
for image_set in sets:
    image_ids = open(fr'data/ImageSets/{image_set}.txt').read().strip().split()
    list_file = open('data/%s.txt' % (image_set), 'w')
    for image_id in image_ids:
        list_file.write('data/JPEGImages/{}\n'.format(image_id + extension[image_id]))
        convert_annotation(image_id)
    list_file.close()

