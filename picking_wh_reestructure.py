# !/usr/bin/env python
# -*- coding: utf-8 -*-
import oerplib
import logging
import datetime
import click
import csv

import psycopg2
_logger = logging.getLogger(__name__)
#############################
# ## Constants Declaration ###
#############################


@click.command()
@click.option('-po', default='admin', prompt='Password of Odoo',
              help='Password of user Odoo')
@click.option('-dbo', default='database', prompt='Database Odoo', help='DB Name')
@click.option('-uo', default='admin', prompt='User Odoo', help='User of odoo')
@click.option('-pod', default=8069, prompt='Port Odoo', help='Port of Odoo')
@click.option('-du', default='odoo', prompt='Database User',
              help='Name of database user')
@click.option('-dp', default='1234', prompt='Database Password',
              help='Password of database user')
@click.option('-dpo', default=5432, prompt='Database Port',
              help='Port of Postgres')
@click.option('-dh', default='localhost', prompt='Database Host',
              help='Host of Postgres')

def change_aml(po, dbo, uo, pod, du, dp, dpo, dh):
    conect = oerplib.OERP('localhost', port=pod)
    conect.login(user=uo, passwd=po, database=dbo)
    conp = psycopg2.connect("dbname='{dn}' user='{du}' host='{dh}' "
                            "password='{dp}' port={dpo}".format(dn=dbo,
                                                                du=du,
                                                                dh=dh,
                                                                dp=dp,
                                                                dpo=dpo))
    purchase_no_confirmed = conect.search('purchase.order', [
        ('state', '=', 'draft')
        ])
    print purchase_no_confirmed, "Purchase Open"
    conect.write('purchase.order', purchase_no_confirmed, {'picking_type_id': 7})
    # picking_type_loc = {1: 1521, 19: 1562}  # se coloca la ubicacion de acuerdo al picking_type
    # for picking_type in picking_type_loc.keys():
    #     purchase_no_confirmed = conect.search('purchase.order', [
    #         ('state', '=', 'draft'),
    #         ('picking_type_id', '=', picking_type)
    #         ])
    #     print purchase_no_confirmed, "purchase on algo"
    #     conect.write('purchase.order', purchase_no_confirmed, {'location_id': picking_type_loc[picking_type]})

    #     purchase_ids = conect.search('purchase.order', [
    #         ('state', '=', "approved"),
    #         ('picking_type_id', '=', picking_type)
    #         ])
    #     for po in conect.browse('purchase.order', purchase_ids):
    #         print po.location_id, "----------before"
    #         conect.write('purchase.order', po.id, {'location_id': picking_type_loc[picking_type]})
    #         print po.location_id, "----------After"
    #         for picking_received in po.picking_ids:
    #             if picking_received.state == 'assigned':
    #                 wz_trans_id = conect.create(
    #                     'stock.transfer_details', {'picking_id': picking_received.id})
    #                 for line in picking_received.move_lines:
    #                     conect.write('stock.move', line.id, {'location_dest_id': picking_type_loc[picking_type]})
    #                     conect.create('stock.transfer_details_items', {
    #                         'quantity': line.product_uom_qty,
    #                         'sourceloc_id': line.location_id.id,
    #                         'destinationloc_id': line.location_dest_id.id,
    #                         'transfer_id': wz_trans_id,
    #                         'product_id': line.product_id.id,
    #                         'product_uom_id': line.product_id.uom_id.id})
    #                 conect.get('stock.transfer_details').do_detailed_transfer(
    #                     [wz_trans_id])
    #             print picking_received.state, "----------picking status"
    #         # Para cancelar el o los restantes de la  orden de compra Entrada->Existencias
    #         conect.get('stock.picking').action_cancel(conect.search('stock.picking', [('origin', 'like', po.name), ('state', '=', 'assigned')]))
if __name__ == '__main__':
    change_aml()
