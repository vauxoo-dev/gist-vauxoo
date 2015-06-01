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
@click.option('-dbo', default='test', prompt='Database Odoo', help='DB Name')
@click.option('-uo', default='admin', prompt='User Odoo', help='User of odoo')
@click.option('-pod', default=8069, prompt='Port Odoo', help='Port of Odoo')
@click.option('-du', default='admin', prompt='Database User',
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

    invoice_line = conect.search('account.invoice.line', [('move_id', '<>', False)])
    for inv_line in conect.browse('account.invoice.line', invoice_line):
        move_line = conect.search('account.move.line', [
                                            ('product_id', '=', inv_line.product_id.id),
                                            ('move_id', '=', inv_line.invoice_id.move_id.id),
                                            ])
        print inv_line.invoice_id.id, inv_line.id, '_', inv_line.price_subtotal, inv_line.move_id
        for line in conect.browse('account.move.line',move_line):
            if inv_line.price_subtotal == line.credit or inv_line.price_subtotal == line.debit or inv_line.price_subtotal == line.amount_currency:
                print line.id, '----', line.amount_currency, line.credit, line.debit

if __name__ == '__main__':
    change_aml()
