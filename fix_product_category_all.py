# -*- encoding: utf-8 -*-
##################################################
# Description:
# - Script to replace 'All products' category from
#   v6 by 'All' category from later versions
#
# coded by: josemiguel@vauxoo.com
##################################################
import oerplib
import argparse

PARSER = argparse.ArgumentParser()
PARSER.add_argument("-d", "--db", help="DataBase Name", required=True)
PARSER.add_argument("-r", "--user", help="OpenERP User", required=True)
PARSER.add_argument("-w", "--passwd", help="OpenERP Password", required=True)
PARSER.add_argument("-p", "--port", type=int,
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

OERP_CONNECT = oerplib.OERP(server=SERVER,
                            database=DB_NAME,
                            protocol='xmlrpc', port=PORT, timeout=4000)

UID_CONF = OERP_CONNECT.login(USER, PASSW)

imd_obj = OERP_CONNECT.get('ir.model.data')
categ_obj = OERP_CONNECT.get('product.category')
tmpl_obj = OERP_CONNECT.get('product.template')


# check if exists 'product.cat0' (v6)
imd_product_cat0 = OERP_CONNECT.search('ir.model.data', [
    ('model', '=', 'product.category'),
    ('module', '=', 'product'),
    ('name', '=', 'cat0')])

if not imd_product_cat0:
    print "Not exists xml id 'product.cat0'"
    quit()

# check if exists 'product.product_category_all' (Up v6)
imd_product_category_all = OERP_CONNECT.search('ir.model.data', [
    ('model', '=', 'product.category'),
    ('module', '=', 'product'),
    ('name', '=', 'product_category_all')])

if not imd_product_category_all:
    print "Not exists xml id 'product.product_category_all'"
    quit()

categ_old_id = imd_obj.browse(imd_product_cat0[0]).res_id
categ_new_id = imd_obj.browse(imd_product_category_all[0]).res_id

# Replace 'product.cat0' from product category
product_categ_ids = OERP_CONNECT.search('product.category', [
    ('parent_id', '=', categ_old_id)])

categ_obj.write(product_categ_ids, {'parent_id': categ_new_id})

# Replace 'product.cat0' from product template
product_tmpl_ids = OERP_CONNECT.search('product.template', [
    ('categ_id', '=', categ_old_id)])
tmpl_obj.write(product_tmpl_ids, {'categ_id': categ_new_id})
