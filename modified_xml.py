import sys
import os
from lxml import etree

def remove_depreciated(files):
    filex = open(files)
    try:
        tree = etree.parse(filex)
    except:
        return True
    read = tree.xpath('//record')
    for line in read:
        types =  line.xpath('//field')
        for data in types:
            dat = data.keys()
            dat.sort()
            if dat == ['model', 'name', 'ref']:
                data.attrib.get('model',False) and data.attrib.pop('model')
                out = open('{}'.format( files ), 'w')
                tree.write(out, xml_declaration=True, encoding='UTF-8')
                out.close()
    return True

path = sys.argv[1]
for dirpath, dnames, fnames in os.walk( path ):
    if '.git' in dirpath:
        continue
    for f in fnames:
        if f.endswith(".xml"):
            fname = (os.path.join(dirpath, f))
            remove_depreciated(fname)