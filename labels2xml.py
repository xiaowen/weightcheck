# Use annotations.csv to regenerate annotations XML files used by labelImg

from lxml import etree
import os
from pdb import set_trace as st

with open('annotations.csv') as csv:
    lines = csv.readlines()[1:]

    for line in lines:
        parts = line.strip().split(',')
        filechunk, width, height = parts[:3]

        root = etree.Element('annotation')
        root.append(etree.XML('<folder>images</folder>'))
        root.append(etree.XML('<filename>%s</filename>' % (filechunk)))
        root.append(etree.XML('<path>%s</path>' % (filechunk)))
        root.append(etree.XML('<source><database>Unknown</database></source>'))
        root.append(etree.XML('<size><width>%s</width><height>%s</height><depth>3</depth></size>' % (width, height)))
        root.append(etree.XML('<segmented>0</segmented>'))

        for i in range(3, len(parts), 5):
            label, xmin, ymin, xmax, ymax = parts[i:i+5]
            obj = etree.Element('object')
            obj.append(etree.XML('<name>%s</name>' % (label)))
            obj.append(etree.XML('<pose>Unspecified</pose>'))
            obj.append(etree.XML('<truncated>0</truncated>'))
            obj.append(etree.XML('<difficult>0</difficult>'))
            obj.append(etree.XML('<bndbox><xmin>%s</xmin><ymin>%s</ymin><xmax>%s</xmax><ymax>%s</ymax></bndbox>' % (xmin, ymin, xmax, ymax)))
            root.append(obj)

        outstr = etree.tostring(root, pretty_print=True)
        with open('images/%s.xml' % (filechunk), 'w') as fid:
            fid.write(outstr)
