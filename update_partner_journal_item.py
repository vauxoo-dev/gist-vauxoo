# Fixed XML when is not decoded
import oerplib
import argparse
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

company_obj = OERP_CONNECT.get('res.company')
aml_obj = OERP_CONNECT.get('account.move.line')
move_obj = OERP_CONNECT.get('account.move')
ait_obj = OERP_CONNECT.get('account.invoice.tax')
invoice_obj = OERP_CONNECT.get('account.invoice')
tax_obj = OERP_CONNECT.get('account.tax')

journal_ids = []
for company in company_obj.browse(company_obj.search([])):
    if company.tax_cash_basis_journal_id:
        journal_ids.append(company.tax_cash_basis_journal_id.id)

invoice_ids = invoice_obj.search([
    ('type', '=', 'in_invoice'),
    ('state', '=', 'paid'),
])

fixeds = []
move_dict = {
    24429: 197,
    24397: 67,
    24515: 82,
    24394: 67,
    24467: 48,
    26915: 77,
    26911: 169,
    26901: 345,
    24374: 72,
    25755: 82,
    25751: 67,
    25748: 67,
    25731: 169,
    25663: 57,
    25135: 20,
    28912: 72,
    28900: 77,
    28896: 170,
    28834: 169,
    28826: 72,
    28822: 70,
    28271: 82,
    24677: 82,
    26963: 56,
    28272: 82,
    24678: 82,
    28166: 39,
    28165: 39,
    28817: 153,
    28824: 71,
    28299: 57,
    24682: 38,
    24680: 33,
    28892: 33,
    28819: 33,
    28224: 33,
    28634: 33,
    26919: 253,
    26905: 334,
    26624: 33,
    26939: 416,
    28898: 334,
    32321: 72,
    33443: 169,
    28621: 69,
    28620: 43,
    24372: 365,
    24594: 346,
}
for move in move_dict:
    OERP_CONNECT.execute('account.move', 'button_cancel', [move])
    lines = move_obj.browse(move).line_ids.ids
    aml_obj.write(lines, {'partner_id': move_dict.get(move)})
    fixeds.extend(lines)
    OERP_CONNECT.execute('account.move', 'post', [move])

taxes = tax_obj.search([('type_tax_use', '=', 'purchase')])
acc_tax = [t.cash_basis_account.id for t in tax_obj.browse(taxes) if t.cash_basis_account]
for journal in journal_ids:
    aml_ids = aml_obj.search([
        ('partner_id', '=', False),
        ('journal_id', '=', journal),
        ('tax_ids', '!=', False),
        ('ref', '=', False),
    ])
    for line in aml_obj.browse(aml_ids):
        tax = tax_obj.browse(line.tax_ids.ids[0])
        if tax.type_tax_use != 'purchase' or line.id in fixeds:
            continue
        move = line.move_id
        invoice = invoice_obj.search(['|', ('amount_untaxed', '=', move.amount), ('amount_total', '=', move.amount), ('state', '=', 'paid')])
        if len(invoice) == 1:
            OERP_CONNECT.execute('account.move', 'button_cancel', [move.id])
            partner = invoice_obj.browse(invoice[0]).partner_id.id
            aml_obj.write(move.line_ids.ids, {'partner_id': partner})
            OERP_CONNECT.execute('account.move', 'post', [move.id])
            fixeds.extend(move.line_ids.ids)
            continue
        elif invoice:
            partner = []
            [partner.append(i.partner_id.id) for i in invoice_obj.browse(invoice) if i.partner_id.id not in partner]
            if len(partner) == 1:
                OERP_CONNECT.execute('account.move', 'button_cancel', [move.id])
                aml_obj.write(move.line_ids.ids, {'partner_id': partner[0]})
                OERP_CONNECT.execute('account.move', 'post', [move.id])
                fixeds.extend(move.line_ids.ids)
                continue
    
