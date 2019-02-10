# https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/using_your_own_dataset.md

import io
import os
from PIL import Image
from pdb import set_trace as st
import sys

import tensorflow as tf
from object_detection.utils import dataset_util

label_map = {
    'scale': 1, 'reading': 2,
    '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '0': 10, '%': 11,
}

def create_record(lines, outrecord):

    writer = tf.python_io.TFRecordWriter(outrecord)
    for line in lines:
        parts = line.strip().split(',')
        filepart,width,height = parts[0], int(parts[1]), int(parts[2])

        lenparts = len(parts)
        texts = [parts[i] for i in range(3, lenparts, 5)]
        labels = [label_map[x] for x in texts]
        xmins = [float(parts[i])/width for i in range(4, lenparts, 5)]
        ymins = [float(parts[i])/height for i in range(5, lenparts, 5)]
        xmaxes = [float(parts[i])/width for i in range(6, lenparts, 5)]
        ymaxes = [float(parts[i])/height for i in range(7, lenparts, 5)]

        # Resize the image to a good size and update features
        imgfile = os.path.join('images', filepart + '.jpg')
        img = Image.open(imgfile)
        img.thumbnail((1000, 1000), Image.ANTIALIAS)
        width, height = img.size
        with io.BytesIO() as output:
            img.save(output, format="JPEG")
            imgbytes = output.getvalue()

        feature = {
            'image/height': dataset_util.int64_feature(height),
            'image/width': dataset_util.int64_feature(width),
            'image/filename': dataset_util.bytes_feature(filepart.encode('utf8')),
            'image/source_id': dataset_util.bytes_feature(filepart.encode('utf8')),
            'image/encoded': dataset_util.bytes_feature(imgbytes),
            'image/format': dataset_util.bytes_feature(b'jpeg'),
            'image/object/bbox/xmin': dataset_util.float_list_feature(xmins),
            'image/object/bbox/xmax': dataset_util.float_list_feature(xmaxes),
            'image/object/bbox/ymin': dataset_util.float_list_feature(ymins),
            'image/object/bbox/ymax': dataset_util.float_list_feature(ymaxes),
            'image/object/class/text': dataset_util.bytes_list_feature([x.encode('utf8') for x in texts]),
            'image/object/class/label': dataset_util.int64_list_feature(labels),
        }

        writer.write(tf.train.Example(features=tf.train.Features(feature=feature)).SerializeToString())

    writer.close()

with open('annotations.csv') as csv:
    lines = csv.readlines()[1:]
    cutoff = len(lines) * 9//10

    print('Putting %s records in train and %s records in test' % (cutoff, len(lines)-cutoff))
    create_record(lines[:cutoff], 'train.record')
    create_record(lines[cutoff:], 'test.record')
