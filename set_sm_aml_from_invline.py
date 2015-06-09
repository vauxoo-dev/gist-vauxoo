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
@click.option('-po', default='4DM1NCHUCK', prompt='Password of Odoo',
              help='Password of user Odoo')
@click.option('-dbo', default='lodi_mayo', prompt='Database Odoo', help='DB Name')
@click.option('-uo', default='nhomar@vauxoo.com', prompt='User Odoo', help='User of odoo')
@click.option('-pod', default=8069, prompt='Port Odoo', help='Port of Odoo')
@click.option('-du', default='odoo', prompt='Database User',
              help='Name of database user')
@click.option('-dp', default='1234', prompt='Database Password',
              help='Password of database user')
@click.option('-dpo', default=5432, prompt='Database Port',
              help='Port of Postgres')
@click.option('-dh', default='localhost', prompt='Database Host',
              help='Host of Postgres')
@click.option('-fini', prompt='Fecha de Inicio',
              help='Fecha de Inicio')
@click.option('-ffin', prompt='Fecha de Fin',
              help='Fecha de Fin')
def change_aml(po, dbo, uo, pod, du, dp, dpo, dh, fini, ffin):
    conect = oerplib.OERP('localhost', port=pod)
    conect.login(user=uo, passwd=po, database=dbo)
    conp = psycopg2.connect("dbname='{dn}' user='{du}' host='{dh}' "
                            "password='{dp}' port={dpo}".format(dn=dbo,
                                                                du=du,
                                                                dh=dh,
                                                                dp=dp,
                                                                dpo=dpo))

    dict_update = {}
    invoice_ids = conect.search('account.invoice', [
        ('date_invoice', '>=', fini),
        ('date_invoice', '<=', ffin)])
    invoice_line = conect.search(
        'account.invoice.line',
        [('invoice_id', 'in', invoice_ids), ('move_id', '<>', False)])
    for inv_line in conect.browse('account.invoice.line', invoice_line):
        move_line = conect.search('account.move.line', [
            ('product_id', '=', inv_line.product_id.id),
            ('move_id', '=', inv_line.invoice_id.move_id.id),
            ('quantity', '=', inv_line.quantity)
            ])
        list_browse_acc_move_lines = conect.read(
            'account.move.line', move_line,
            ['credit', 'debit', 'amount_currency'])
        sum_cred = sum(
            [line.get('credit') for line in list_browse_acc_move_lines])
        sum_deb = sum(
            [line.get('debit') for line in list_browse_acc_move_lines])
        sum_amount = sum(
            [line.get(
                'amount_currency') for line in list_browse_acc_move_lines])
        for line in list_browse_acc_move_lines:
            if inv_line.price_subtotal in line.values():
                conect.write(
                    'account.move.line', line.get('id'),
                    {'sm_id': inv_line.move_id.id})
                dict_update[line.get('id')] = inv_line.move_id.id
            elif inv_line.price_subtotal in [sum_cred, sum_deb, sum_amount]:
                conect.write(
                    'account.move.line', line.get('id'),
                    {'sm_id': inv_line.move_id.id})
                dict_update[line.get('id')] = inv_line.move_id.id
    print dict_update
if __name__ == '__main__':
    change_aml()
