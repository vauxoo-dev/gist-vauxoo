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

    product_ids = conect.search(
        'product.product', [('valuation', '=', 'real_time')])
    move_ids = conect.search(
        'stock.move', [
            ('product_id', 'in', product_ids),
            ('picking_id', '!=', False),
            ('state', '=', 'done')])
    pick_ids = []
    file_new = open('/tmp/moves_changeds.csv', 'wb')
    file_new.write('id, name, date, period\n')
    for move in conect.read('stock.move', move_ids, ['date', 'picking_id']):
        if move.get('picking_id')[0] in pick_ids:
            continue
        else:
            pick_ids.append(move.get('picking_id')[0])
        date_move = datetime.datetime.strptime(
            str(move.get('date')), '%Y-%m-%d %H:%M:%S').date().strftime(
            '%Y-%m-%d')
        account_period_obj = conect.get('account.period')
        period_date = account_period_obj.find(dt=date_move, context={})
        acc_m_ids = conect.search(
            'account.move', [
                ('ref', '=', move.get('picking_id')[1]),
                ('period_id', '!=', period_date[0])
            ])
        for acc_mv in conect.browse('account.move', acc_m_ids):
            cr = conp.cursor()
            cr.execute("""UPDATE account_move
                          SET period_id={pid}, date='{dte}'
                          WHERE id={amid}""".format(
                pid=period_date[0], dte=date_move, amid=acc_mv.id))
            for line in acc_mv.line_id:
                cr.execute("""UPDATE account_move_line
                          SET period_id={pid}, date='{dte}'
                          WHERE id={amlid}""".format(
                    pid=period_date[0], dte=date_move, amlid=line.id))
            file_new.write('%s, %s, %s, %s\n' % (
                acc_mv.id, acc_mv.name, acc_mv.date, acc_mv.period_id.id or ''))
    file_new.close()
    conp.commit()

if __name__ == '__main__':
    change_aml()
