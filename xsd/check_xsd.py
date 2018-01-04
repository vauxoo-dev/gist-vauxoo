from io import BytesIO
from lxml import etree

schema_str = open('/Users/luistorres/Documents/xsd/cfdv33.xsd').read()
xml_valid = open('/Users/luistorres/Documents/xsd/xml.xml').read()
with BytesIO(schema_str) as xsd:
    schema_root = etree.parse(xsd)
schema = etree.XMLSchema(schema_root)
try:
    print '1'
    tree = etree.fromstring(xml_valid.encode('UTF-8'))
    print '2'
    schema.assertValid(tree)
    print '3'
except etree.DocumentInvalid as ups:
    print ups
