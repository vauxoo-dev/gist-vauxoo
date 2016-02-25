#!/usr/bin/env python
# -*- coding: utf-8 -*-
import oerplib
import argparse
import logging

_logger = logging.getLogger(__name__)

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
    "-s", "--server",
    help="Server IP, 127.0.0.1 for default", default="127.0.0.1")
parser.add_argument("-D", "--db2", help="Second DataBase Name", required=True)
parser.add_argument("-R", "--user2", help="Second OpenERP User", required=True)
parser.add_argument(
    "-W", "--passwd2", help="Second OpenERP Password", required=True)
parser.add_argument(
    "-P", "--port2", type=int,
    help="Second Port, 8069 for default", default="8069")
parser.add_argument(
    "-S", "--server2",
    help="Second Server IP, 127.0.0.1 for default", default="127.0.0.1")
args = parser.parse_args()

if(args.db is None or args.user is None or args.passwd is None ):
    print "Must be specified DataBase, User and Password"
    quit()

db_name2 = args.db2
user2 = args.user2
passwd2 = args.passwd2
port2 = args.port2
server2 = args.server2
connect2 = oerplib.OERP(
    server=server2,
    database=db_name2,
    port=port2,)
connect2.login(user2, passwd2)
connect2.config['timeout'] = 1000000

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
domain = [
    # ('model_id', '=', 'stock.picking')
]
model = 'res.groups'
groups= connect.browse(model, connect.search(model, domain))
groups2 = connect2.browse(model, connect2.search(model, domain))
# if the difference is set([elements])
set_groups = set(groups.ids).difference(groups2.ids)
set_groups2 = set(groups2.ids).difference(groups.ids)
if set_groups or set_groups2:
    print "##############################################################################"
    print "There are differences beetwen instances, one or more res.groups are different"
    print "Instance %s:%d res_groups_ids different = %s" %( server, port, list(set_groups))
    print "Instance %s:%d res_groups_ids different = %s" %( server2, port2, list(set_groups2))
    # if there are differences, show the groups
    if set_groups:
        group_different = connect.browse(model, list(set_groups))
        print "Name groups and users"
        for gr in group_different:
            print {'id': gr.id, 'name': gr.name, 'users_ids': gr.users.ids}
    if set_groups2:
        group_different = connect.browse(model, list(set_groups2))
        print "Name groups and users"
        for gr in group_different:
            print {'id': gr.id, 'name': gr.name, 'users_ids': gr.users.ids}
    print "##############################################################################"
else:
    print "Res.groups are not different"
    print "Instance %s:%d res_groups_ids different = %s" %( server, port, list(set_groups))
    print "Instance %s:%d res_groups_ids different = %s" %( server2, port2, list(set_groups2))

groups= connect.browse(model, connect.search(model, domain))
groups2 = connect2.browse(model, connect2.search(model, domain))
users = dict((group.id, group.users.ids) for group in groups if group.id not in list(set_groups))
users2 = dict((group.id, group.users.ids) for group in groups2 if group.id not in list(set_groups2))
flag = False
for indx, item in enumerate(users):
    set_users = users[item]
    set_users2 = users2[item]
    try:
        assert set(set_users).difference(
            set_users2) == set(set_users2).difference(set_users)
    except:
        flag = True
        print "There are diferences beetwen group's users:"
        print "for res_group_id = %s" %(item)
        print "Instance %s:%d res_users_ids differents = %s" %( server, port, set(set_users2).difference(set_users))
        print "Instance %s:%d res_users_ids differents = %s" %( server2, port2, set(set_users).difference(set_users2))
        print "##############################################################################"
if not flag:
    print "res.groups and res.users of each group, was validated, see details above"
