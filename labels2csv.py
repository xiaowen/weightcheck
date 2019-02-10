from __future__ import print_function
import glob
from lxml import etree
import os
from pdb import set_trace as st

outfile = open('annotations.csv', 'w')
print('file,width,height,label1,xmin,ymin,xmax,ymax,label2,xmin,ymin,xmax,ymax,...', file=outfile)
for xmlfile in glob.glob('images/*.xml'):
    line = []

    # Read the XML (annotation) files and parse
    with open(xmlfile) as f:
        xml = f.read()
    root = etree.XML(xml)

    line.append(xmlfile.split('/')[-1][:-4])
    line.append(root.xpath('//size/width')[0].text)
    line.append(root.xpath('//size/height')[0].text)

    for obj in root.xpath('//object'):
        line.append(obj.xpath('./name')[0].text)
        line.append(obj.xpath('./bndbox/xmin')[0].text)
        line.append(obj.xpath('./bndbox/ymin')[0].text)
        line.append(obj.xpath('./bndbox/xmax')[0].text)
        line.append(obj.xpath('./bndbox/ymax')[0].text)

    # Some sanity checks
    if len(line) == 13:
        assert(line[3] == 'scale')
        assert(line[8] == 'reading')
        assert(int(line[4]) < int(line[9]))
        assert(int(line[5]) < int(line[10]))
        assert(int(line[6]) > int(line[11]))
        assert(int(line[7]) > int(line[12]))

    elif len(line) == 23:
        if line[18] == '%':
            for index in [3, 8, 13]:
                assert(int(line[index]) in [x for x in range(10)])
        else:
            for index in [3, 8, 13, 18]:
                assert(int(line[index]) in [x for x in range(10)])

    print(','.join(line), file=outfile)

outfile.close()
