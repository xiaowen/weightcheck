# Derived from models/research/object_detection/object_detection_tutorial.ipynb

from __future__ import print_function
import glob
import numpy as np
import os
import tensorflow as tf
import object_detection.utils.label_map_util as label_map_util
from pdb import set_trace as st
from PIL import Image
import sys

workdir = os.getcwd().split('/')[-1]

detection_graph = tf.Graph()
with detection_graph.as_default():
    od_graph_def = tf.GraphDef()
    with tf.gfile.GFile('model/exported_graphs/frozen_inference_graph.pb', 'rb') as fid:
        serialized_graph = fid.read()
        od_graph_def.ParseFromString(serialized_graph)
        tf.import_graph_def(od_graph_def, name='')

category_index = label_map_util.create_category_index_from_labelmap('labels.pbtxt', use_display_name=True)

bboxfile = 'detectedbboxes.csv'
if os.path.exists(bboxfile):
    with open(bboxfile, 'r') as fid:
        known_bboxes = [x.strip().split(',', 1) for x in fid.readlines()[1:]]
        known_bboxes = dict((x[0], x[1]) for x in known_bboxes)
else:
    known_bboxes = dict()

for jpg in glob.glob('images/*.jpg'):
    ipart = jpg.split('/')[-1][:-4]
    if ipart in known_bboxes:
        continue

    print('Processing: ' + ipart)
    image = Image.open(jpg)

    # Perform detection
    smaller = image.copy()
    smaller.thumbnail((1000, 1000), Image.ANTIALIAS)
    im_width, im_height = smaller.size
    image_np = np.array(smaller.getdata()).reshape((im_height, im_width, 3)).astype(np.uint8)
    with detection_graph.as_default():
        with tf.Session() as sess:
            image_tensor = tf.get_default_graph().get_tensor_by_name('image_tensor:0')
            output = sess.run(
                ['num_detections:0', 'detection_boxes:0', 'detection_scores:0', 'detection_classes:0'],
                feed_dict={image_tensor: np.expand_dims(image_np, 0)})

            num_detections = int(output[0][0])
            detection_boxes = output[1][0]
            detection_scores = output[2][0]
            detection_classes = output[3][0].astype(np.uint8)

    if workdir.startswith('scale'): boxcount = 2
    elif workdir.startswith('reading'): boxcount = 4
    else: assert(False)

    if any(detection_scores[:boxcount] < 0.9):
        print(ipart + ': boxes not detected')
        continue

    # Collect data
    w, h = image.size
    outline = [w, h]
    for i in range(boxcount):
        ymin, xmin, ymax, xmax = detection_boxes[i]
        label = category_index[detection_classes[i]]['name']
        outline += [label, detection_scores[i], xmin, ymin, xmax, ymax]
    outlinestr = ','.join(map(str, outline))

    # Sanity checks
    if workdir.startswith('scale'):
        if sorted(detection_classes[:2]) != [1,2]:
            print('Wrong boxes detected: %s,%s' % (ipart, outlinestr))
            continue

    elif workdir.startswith('reading'):
        xmins = outline[4], outline[10], outline[16], outline[22]
        xmaxs = outline[6], outline[12], outline[18], outline[24]
        if not all(0.05 < (xmaxs[i]-xmins[i]) < 0.2 for i in range(4)):
            print('Boxes wrong width: %s,%s' % (ipart, outlinestr))
            continue

        xmins, xmaxs = sorted(list(xmins)), sorted(list(xmaxs))
        if not all(-0.03 < (xmins[i+1] - xmaxs[i]) < (i < 2 and 0.05 or 0.1) for i in range(3)):
            print('Boxes wrong overlap: %s,%s' % (ipart, outlinestr))
            continue

    known_bboxes[ipart] = outlinestr

with open(bboxfile, 'w') as fid:
    print('file,width,height,label1,score1,xmin,ymin,xmax,ymax,label2,score2,xmin,ymin,xmax,ymax,...', file=fid)
    for ipart in sorted(known_bboxes):
        print('%s,%s' % (ipart, known_bboxes[ipart]), file=fid)
