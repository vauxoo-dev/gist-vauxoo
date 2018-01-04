from __future__ import print_function

from lxml import etree

schema_str = open('./cfdv33.xsd')
xml_valid = open('./xml.xml')
schema_root = etree.parse(schema_str)
schema = etree.XMLSchema(schema_root)
try:
    print('1')
    tree = etree.parse(xml_valid)
    print('2')
    schema.assertValid(tree)
    print('3')
except etree.DocumentInvalid as ups:
    print(ups)
