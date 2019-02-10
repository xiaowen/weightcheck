import os
from pdb import set_trace as st
from PIL import Image

with open('scale/detectedbboxes.csv', 'r') as csv:
    for line in csv.readlines()[1:]:
        line = line.strip().split(',')
        ipart, w, h = line[0], int(line[1]), int(line[2])
        outpath = 'reading/images/' + ipart + '.jpg'
        if os.path.exists(outpath):
            continue

        print('Processing: ' + ipart)
        image = Image.open('scale/images/' + ipart + '.jpg')
        assert(w == image.size[0])
        assert(h == image.size[1])

        for i in range(3, len(line), 6):
            if line[i] == 'reading':
                xmin,ymin,xmax,ymax = map(float, line[i+2:i+6])
                rbox = image.crop((xmin*w, ymin*h, xmax*w, ymax*h))
                rbox.save(outpath)
