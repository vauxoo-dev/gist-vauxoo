#!/usr/bin/env python
# -*- coding: utf-8 -*-
##################################################
# Description:
# - Script to update translations
#
# coded by: hugo@vauxoo.com
##################################################
import oerplib
import argparse
import logging

_logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser()
parser.add_argument("-d", "--db", help="DataBase Name", required=True)
parser.add_argument("-r", "--user", help="Odoo User", required=True)
parser.add_argument("-w", "--passwd", help="Odoo Password", required=True)
parser.add_argument("-p", "--port", type=int, help="Port, 8069 for default",
                    default="8069")
parser.add_argument("-s", "--server", help="Server IP, 127.0.0.1 for default",
                    default="127.0.0.1")
args = parser.parse_args()

if args.db is None or args.user is None or args.passwd is None:
    _logger.danger("Must be specified DataBase, User and Password")
    quit()

db_name = args.db
user = args.user
passwd = args.passwd
server = args.server
port = args.port
connect = oerplib.OERP(
    server=server,
    database=db_name,
    port=port,)
connect.login(user, passwd)
connect.config['timeout'] = 1000000

base_lenguage = connect.get('base.language.install')
website_obj = connect.get('website')
website = website_obj.search([], limit=1)[0]
wizard_id = base_lenguage.create(
    {'lang': 'es_MX', 'overwrite': True, 'website_ids': [(4, [website])]})

wizard = base_lenguage.lang_install([wizard_id])
_logger.info('DONE')
