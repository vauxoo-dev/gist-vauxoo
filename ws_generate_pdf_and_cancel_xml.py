# coding: utf-8

import os
import odoorpc
import argparse
import base64

PARSER = argparse.ArgumentParser(
    description="Generate Payroll PDF and Cancel XML")
PARSER.add_argument("-d", "--db", help="DataBase Name", required=True)
PARSER.add_argument("-r", "--user", help="OpenERP User", required=True)
PARSER.add_argument("-w", "--passwd", help="OpenERP Password", required=True)
PARSER.add_argument("-p", "--port",
                    type=int,
                    help="Port, 8069 for default", default="8069")
PARSER.add_argument("-s", "--server",
                    help="Server IP, 127.0.0.1 for default",
                    default="127.0.0.1")
PARSER.add_argument("-dir", "--directory", help="XML Directory path",
                    required=True)
PARSER.add_argument("-o", "--output", help="Output directory")
ARGS = PARSER.parse_args()

if ARGS.db is None or ARGS.user is None or ARGS.passwd is None or ARGS.directory is None:
    print "Must be specified DataBase, User, Password and Directory path"
    quit()

if not os.path.isdir(ARGS.directory) or (ARGS.output and not os.path.isdir(ARGS.output)):
    print "The specified directory must exist"
    quit()

DB_NAME = ARGS.db
USER = ARGS.user
PASSWD = ARGS.passwd
SERVER = ARGS.server
PORT = ARGS.port
URL = 'http://%s:%s' % (SERVER, PORT)
XML_DIR = ARGS.directory
OUTPUT_DIR = ARGS.output
if not OUTPUT_DIR:
    OUTPUT_DIR = XML_DIR

odoo = odoorpc.ODOO(SERVER, port=PORT)
odoo.login(DB_NAME, USER, PASSWD)
odoo.env.context['lang'] = 'es_MX'
payslip = odoo.env['hr.payslip']
payslip_id = payslip.search([], limit=1)[0]

for filename in os.listdir(XML_DIR):
    if not filename.endswith('.xml'):
        continue
    payslip_copy = payslip.copy(payslip_id)
    payslip_new = payslip.browse(payslip_copy)
    payslip_new = payslip_new.hr_verify_sheet()
    attach_facturae = odoo.env['ir.attachment.facturae.mx'].browse(
        payslip_new['res_id'])
    xml_location = os.path.join(XML_DIR, filename)
    with open(xml_location, 'r') as open_file:
        file_data = open_file.read()
        attach_new = odoo.env['ir.attachment'].create({
            'type': 'binary',
            'name': filename,
            'datas': base64.encodestring(file_data), })
    attach_facturae.write({
        'file_xml_sign': attach_new,
        'state': 'signed',
    })
    attach_facturae.signal_printable()
    if attach_facturae.file_pdf:
        attach_facturae.write({'state': 'printable'})
        fname_pdf = attach_facturae.file_xml_sign.name.replace('xml', 'pdf')
        output = os.path.join(OUTPUT_DIR, fname_pdf)
        with open(output, 'w') as open_file:
            open_file.write(base64.decodestring(
                attach_facturae.file_pdf.datas))
