# -*- encoding: utf-8 -*-
import oerplib
import argparse
import random

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

sale_obj =  OERP_CONNECT.get('sale.order')
pick_obj =  OERP_CONNECT.get('stock.picking')
st_cpq_obj = OERP_CONNECT.get('stock.change.product.qty')
det_tran_obj = OERP_CONNECT.get('stock.transfer_details')

# You need:
# - Install procurement_jit
# - Configure warehouse to 3 steps

sale = sale_obj.create({
    'partner_id': OERP_CONNECT.search('res.partner', [])[0],
})
for product in OERP_CONNECT.search('product.product', []):
    OERP_CONNECT.create('sale.order.line', {
        'order_id': sale,
        'product_id': product,
        'name': product,
        'product_uom_qty': random.randrange(1, 25),
    })
sale = sale_obj.browse(sale)
pickings = sale.picking_ids

ware = sale.warehouse_id
pick_w = ware.pick_type_id.id
pack_w = ware.pack_type_id.id
out_w = ware.out_type_id.id
loc_src = ware.pick_type_id.default_location_src_id.id

for prod in OERP_CONNECT.search('product.product', []):
    wiz = st_cpq_obj.create({
        'product_id': prod,
        'location_id': loc_src,
        'new_quantity': 0,
    })
    st_cpq_obj.change_product_qty(wiz)
# Inicialice todos los productos a 0
for a in range(0, 5):
    sale = sale_obj.browse(sale.id)
    pick = pick_obj.search([
        ('id', 'in', sale.picking_ids.ids),
        ('picking_type_id', '=', pick_w),
        ('state', '!=', 'done'),
    ])
    if pick:
        for prod in OERP_CONNECT.search('product.product', []):
            wiz = st_cpq_obj.create({
                'product_id': prod,
                'location_id': loc_src,
                'new_quantity': 1,
            })
            st_cpq_obj.change_product_qty(wiz)
        pick_obj.action_assign(pick)
        wiz = det_tran_obj.create({'picking_id': pick[0]}, context={
            'active_id': pick[0],
            'active_ids': pick,
            'active_model': 'stock.picking'
        })
        det_tran_obj.do_detailed_transfer(wiz)
# Genere 5 picks
pack = pick_obj.search([
    ('id', 'in', sale.picking_ids.ids),
    ('picking_type_id', '=', pack_w),
])
pick_obj.action_assign(pack)
wiz = det_tran_obj.create({'picking_id': pack[0]}, context={
    'active_id': pack[0],
    'active_ids': pack,
    'active_model': 'stock.picking'
})
det_tran_obj.do_detailed_transfer(wiz)
# Transfiero el pack
for a in range(0, 5):
    sale = sale_obj.browse(sale.id)
    pick = pick_obj.search([
        ('id', 'in', sale.picking_ids.ids),
        ('picking_type_id', '=', pick_w),
        ('state', '!=', 'done'),
    ])
    if pick:
        for prod in OERP_CONNECT.search('product.product', []):
            wiz = st_cpq_obj.create({
                'product_id': prod,
                'location_id': loc_src,
                'new_quantity': 1,
            })
            st_cpq_obj.change_product_qty(wiz)
        pick_obj.action_assign(pick)
        wiz = det_tran_obj.create({'picking_id': pick[0]}, context={
            'active_id': pick[0],
            'active_ids': pick,
            'active_model': 'stock.picking'
        })
        det_tran_obj.do_detailed_transfer(wiz)
# Transfiero otros 5 picks
pack = pick_obj.search([
    ('id', 'in', sale.picking_ids.ids),
    ('picking_type_id', '=', pack_w),
    ('state', '!=', 'done'),
])
pick_obj.action_assign(pack)
wiz = det_tran_obj.create({'picking_id': pack[0]}, context={
    'active_id': pack[0],
    'active_ids': pack,
    'active_model': 'stock.picking'
})
det_tran_obj.do_detailed_transfer(wiz)
# Transfiero el Pack
out = pick_obj.search([
    ('id', 'in', sale.picking_ids.ids),
    ('picking_type_id', '=', out_w),
    ('state', '!=', 'done'),
])
pick_obj.action_assign(out)
wiz = det_tran_obj.create({'picking_id': out[0]}, context={
    'active_id': out[0],
    'active_ids': out,
    'active_model': 'stock.picking'
})
det_tran_obj.do_detailed_transfer(wiz)
# transfiero el out
sale = sale_obj.browse(sale.id)
pick = pick_obj.search([
    ('id', 'in', sale.picking_ids.ids),
    ('state', '!=', 'done'),
])
pick_obj.action_cancel(pick)
