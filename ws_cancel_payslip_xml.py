# coding: utf-8

import argparse
import base64
import os
import odoorpc
import logging
_logger = logging.getLogger(__name__)
try:
    from suds.client import Client
except ImportError:
    _logger.debug('Can not import suds.')


PARSER = argparse.ArgumentParser(description="Cancel Payroll XML")
PARSER.add_argument("-d", "--db", help="DataBase Name", required=True)
PARSER.add_argument("-r", "--user", help="OpenERP User", required=True)
PARSER.add_argument("-w", "--passwd", help="OpenERP Password", required=True)
PARSER.add_argument("-p", "--port",
                    type=int,
                    help="Port, 8069 for default", default="8069")
PARSER.add_argument("-s", "--server",
                    help="Server IP, 127.0.0.1 for default",
                    default="127.0.0.1")
PARSER.add_argument("-f", "--filename", help="XML to cancel file path",
                    required=True)
PARSER.add_argument("-o", "--output", help="Output directory")
PARSER.add_argument("-c", "--copy", help="Payslip to copy")
ARGS = PARSER.parse_args()

if ARGS.db is None or ARGS.user is None or ARGS.passwd is None or ARGS.filename is None:
    print "Must be specified DataBase, User, Password and Directory path"
    quit()

if not os.path.isfile(ARGS.filename):
    print "The specified file must exist"
    quit()

DB_NAME = ARGS.db
USER = ARGS.user
PASSWD = ARGS.passwd
SERVER = ARGS.server
PORT = ARGS.port
URL = 'http://%s:%s' % (SERVER, PORT)
FILE = ARGS.filename
OUTPUT_DIR = ARGS.output

odoo = odoorpc.ODOO(SERVER, port=PORT)
odoo.login(DB_NAME, USER, PASSWD)

cert_location = '/home/odoo/odoo-mexico-v2/l10n_mx_facturae_cer/demo/'
cert_file = 'res_company_facturae_certificate.cer'
cert_key = 'res_company_facturae_certificate.key'
uuids = []
msg = ''
dict_error = {
    '203': 'UUID does not match the RFCsender neither of the applicant',
    '205': 'Not exist UUID',
    '708': 'Could not connect to the SAT'}
pac_params_obj = odoo.env['params.pac']
data_user = odoo.env['res.users'].browse(odoo.env.uid)
taxpayer_id = data_user.company_id.vat[2::]
res_pac_id = odoo.env['res.pac'].search(
    [('company_id', '=', data_user.company_id.id)])
pac_params_ids = pac_params_obj.search([
    ('method_type', '=', 'cancelar'),
    ('res_pac', '=', res_pac_id),
    ('company_id', '=', data_user.company_id.id),
    ('active', '=', True), ], limit=1)
pac_params_id = pac_params_ids and pac_params_ids[0] or False
if not pac_params_id:
    print "Check you PAC parameters"
    quit()
pac_params_brw = pac_params_obj.browse(pac_params_id)[0]
username = pac_params_brw.user
password = pac_params_brw.password
wsdl_url = pac_params_brw.url_webservice
__import__('pdb').set_trace()

with open(os.path.join(cert_location, cert_file), 'r') as open_file:
    cer_csd = open_file.read()

with open(os.path.join(cert_location, cert_key), 'r') as open_file:
    rsa = open_file.read()
key_csd = base64.encodestring(rsa)

try:
    client = Client(wsdl_url, cache=None)
except:
    print "Connection lost, verify your internet connection or verify your PAC"
    raise

with open(FILE, 'r') as open_file:
    for line in open_file:
        uuids.append(line.strip())
        uuids_list = client.factory.create("UUIDS")

uuids_list.uuids.string = uuids
result = client.service.cancel(uuids_list, 'odoo',
                               'AniaAle1', taxpayer_id,
                               base64.encodestring(cer_csd),
                               key_csd)
if 'Folios' not in result:
    print "Warning Message: %s" % (result)
    quit()
else:
    if result.Folios[0][0].EstatusUUID in ('201', '202'):
        print "The process of cancellation has completed correctly"
