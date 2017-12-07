# coding: utf-8

import argparse
import base64
import os
import time
import logging
_logger = logging.getLogger(__name__)
try:
    from suds.client import Client
except ImportError:
    _logger.debug('Can not import suds.')


PARSER = argparse.ArgumentParser(description="Cancel Payroll XML")
PARSER.add_argument("-u", "--pacuser", help="PAC User", required=True)
PARSER.add_argument("-p", "--pacpass", help="PAC Password", required=True)
PARSER.add_argument("-t", "--taxpayer", help="Tax Payer VAT", required=True)
PARSER.add_argument("-w", "--pacurl", help="PAC url",
                    default="http://demo-facturacion.finkok.com/servicios/soap/cancel.wsdl")
PARSER.add_argument("-f", "--filename", help="XML to cancel file path",
                    required=True)
PARSER.add_argument("-o", "--output", help="Output directory")
ARGS = PARSER.parse_args()

if ARGS.pacuser is None or ARGS.pacpass is None or ARGS.taxpayer is None or ARGS.filename is None:
    print "Must be specified PAC User, PAC Password, Tax Payer and Directory path"
    quit()

if not os.path.isfile(ARGS.filename):
    print "The specified file must exist"
    quit()

PACUSER = ARGS.pacuser
PACPASS = ARGS.pacpass
PACURL = ARGS.pacurl
TAXPAYER = ARGS.taxpayer
FILE = ARGS.filename
OUTPUT_DIR = ARGS.output

cert_location = '/home/odoo/odoo-mexico-v2/l10n_mx_facturae_cer/demo/'
cert_file = 'res_company_facturae_certificatepem'
cert_key = 'res_company_facturae_certificatepemkey'
uuids = []
cancel_results = []
dict_error = {
    '000': 'UUID No encontrado',
    '203': 'UUID does not match the RFCsender neither of the applicant',
    '205': 'Not exist UUID',
    '708': 'Could not connect to the SAT',
    '201': 'Cancellation process has completly correctly',
    '202': 'Cancellation process has completly correctly'}

with open(os.path.join(cert_location, cert_file), 'r') as open_file:
    cer_csd = open_file.read()

with open(os.path.join(cert_location, cert_key), 'r') as open_file:
    rsa = open_file.read()
key_csd = base64.encodestring(rsa)

try:
    client = Client(PACURL, cache=None)
except:
    print "Connection lost, verify your internet connection or verify your PAC"
    raise

with open(FILE, 'r') as open_file:
    for line in open_file:
        uuids.append(line.strip())

uuids_list = client.factory.create("UUIDS")
uuids_list.uuids.string = uuids
results = client.service.cancel(uuids_list, PACUSER,
                                PACPASS, TAXPAYER,
                                base64.encodestring(cer_csd),
                                key_csd)
if 'Folios' not in results:
    print results.CodEstatus
    quit()

estatus_uuid = [[d['UUID'], d['EstatusUUID']] for d in results.Folios.Folio]
for uuid in uuids:
    if uuid not in [d[0] for d in estatus_uuid]:
        estatus_uuid.append([uuid, '000'])
for estatus in estatus_uuid:
    if estatus[0] not in uuids:
        cancel_results.append(''.join([estatus[0], ": No encontrado\n"]))
    if estatus[1] in dict_error:
        cancel_results.append(''.join(
                [estatus[0], ": ", dict_error[estatus[1]], "\n"]))
with open(FILE, 'w') as open_file:
    open_file.writelines(cancel_results)
