#!/usr/bin/env python
# -*- coding: utf-8 -*-
import oerplib
import argparse

#############################
# ## Constants Declaration ###
#############################

parser = argparse.ArgumentParser()
parser.add_argument("-d", "--db", help="DataBase Name", required=True)
parser.add_argument("-r", "--user", help="OpenERP User", required=True)
parser.add_argument("-w", "--passwd", help="OpenERP Password", required=True)
parser.add_argument(
    "-p", "--port", type=int, help="Port, 8069 for default", default="8069")
parser.add_argument(
    "-s", "--server", help="Server IP, 127.0.0.1 for default",
    default="127.0.0.1")
args = parser.parse_args()

if(args.db is None or args.user is None or args.passwd is None):
    print "Must be specified DataBase, User and Password"
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

payslip_list = connect.search('hr.payslip', [('state', '=', 'done')])
for payslip in connect.browse('hr.payslip', payslip_list):
    test_paid = connect.execute('hr.payslip', 'test_paid', payslip.id)
    connect.write('hr.payslip', payslip.id, {'reconciled': test_paid})
