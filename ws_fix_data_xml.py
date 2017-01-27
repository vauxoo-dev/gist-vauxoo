# Fixed XML when is not decoded
import oerplib
import argparse
import base64
from lxml import objectify
from codecs import BOM_UTF8
BOM_UTF8U = BOM_UTF8.decode('UTF-8')

PARSER = argparse.ArgumentParser()
PARSER.add_argument("-d", "--db", help="DataBase Name", required=True)
PARSER.add_argument("-r", "--user", help="OpenERP User", required=True)
PARSER.add_argument("-w", "--passwd", help="OpenERP Password", required=True)
PARSER.add_argument("-p", "--port",
                    type=int,
                    help="Port, 8069 for default", default="8069")
PARSER.add_argument("-s", "--server",
                    help="Server IP, 127.0.0.1 for default",
                    default="127.0.0.1")
ARGS = PARSER.parse_args()

if ARGS.db is None or ARGS.user is None or ARGS.passwd is None:
    print "Must be specified DataBase, User and Password"
    quit()

DB_NAME = ARGS.db
USER = ARGS.user
PASSW = ARGS.passwd
SERVER = ARGS.server
PORT = ARGS.port

OERP_CONNECT = oerplib.OERP(SERVER,
                            database=DB_NAME,
                            protocol='xmlrpc', port=PORT)
OERP_CONNECT.config['timeout'] = 600  # Set the timeout to 300 seconds

UID_CONF = OERP_CONNECT.login(USER, PASSW)

invoice_ids = OERP_CONNECT.get('account.invoice').search_read([], ['xml_signed'])

for record in invoice_ids:
    if not record.get('xml_signed'):
        continue
    try:
        objectify.fromstring(record.get('xml_signed').lstrip(BOM_UTF8U).encode("UTF-8"))
    except:
        OERP_CONNECT.get('account.invoice').write(record.get('id'), {'xml_signed': base64.decodestring(record.get('xml_signed'))})
        attachment = OERP_CONNECT.get('ir.attachment').search([
            ('mimetype', '=', 'application/xml'),
            ('res_model', '=', 'account.invoice'),
            ('res_id', '=', record.get('id'))])
        for att in OERP_CONNECT.get('ir.attachment').browse(attachment):
            if not att.datas:
                continue
            try:
                objectify.fromstring(att.datas.encode("UTF-8"))
            except Exception as ex:
                OERP_CONNECT.get('ir.attachment').write(att.id, {'datas': base64.encodestring(base64.decodestring(att.datas).decode("UTF-8").encode("UTF-8"))})
