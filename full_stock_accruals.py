# !/usr/bin/env python
# -*- coding: utf-8 -*-
import oerplib
import logging
import datetime
import click

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
@click.option('-fini', prompt='Fecha de Inicio (dd/mm/yyyy)',
              help='Fecha de Inicio')
@click.option('-ffin', prompt='Fecha de Fin (dd/mm/yyyy)',
              help='Fecha de Fin')
def memoize(func):
    """
    Pro python Marty Alchin, Pag  75, Memoization
    """
    cache = {}

    @functools.wraps(func)
    def wrapper(*args):
        if args in cache:
            return cache[args]
        result = func(*args)
        cache[args] = result
        return result
    return wrapper


def change_aml(po, dbo, uo, pod, du, dp, dpo, dh, fini, ffin):
    conect = oerplib.OERP('localhost', port=pod)
    conect.login(user=uo, passwd=po, database=dbo)
    ffin = datetime.datetime.strptime(ffin, '%d/%m/%Y').strftime('%m/%d/%Y')
    fini = datetime.datetime.strptime(fini, '%d/%m/%Y').strftime('%m/%d/%Y')
    product_ids = conect.search(
        'product.product', [('valuation', '=', 'real_time')])
    move_ids = conect.search(
        'stock.move', [
            ('product_id', 'in', product_ids),
            ('picking_id', '!=', False),
            ('state', '=', 'done'),
            ('date', '>=', fini),
            ('date', '<=', ffin)])
    pick_ids = []
    file_new = open('/tmp/moves_changeds.csv', 'wb')
    file_new.write('id, name, date, period\n')
    for move in conect.read('stock.move', move_ids, ['id', 'date', 'picking_id']):
        if move.get('picking_id')[0] in pick_ids:
            continue
        else:
            pick_ids.append(move.get('picking_id')[0])
        date_move = datetime.datetime.strptime(
            str(move.get('date')), '%Y-%m-%d %H:%M:%S').date().strftime(
            '%Y-%m-%d')
        account_period_obj = conect.get('account.period')
        period_date = account_period_obj.find(dt=date_move, context={})
        period_state = account_period_obj.browse(period_date[0]).state
        acc_m_ids = conect.search(
            'account.move', [
                ('ref', '=', move.get('picking_id')[1]),
                ('period_id', '=', period_date[0])
            ])
        if period_state == "done" and acc_m_ids:
            account_period_obj.action_draft(period_date)
        for acc_mv in conect.browse('account.move', acc_m_ids):
            conect.write("account.move.line", acc_mv.line_id.ids, {'sm_id': move.get("id")})
            file_new.write('%s, %s\n' % (
                 str(acc_mv.line_id.ids), str(move.get("id")) or ''))
        if period_state == "done":
            wizard_period_close_id = conect.create('account.period.close', {'sure': 1})
            conect.execute('account.period.close', 'data_save', [wizard_period_close_id], {
                'lang': 'en_US',
                'active_model': 'account.period',
                'active_ids': period_date,
                'tz': False,
                'active_id': period_date
            })
    file_new.close()

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
        list_browse_acc_move_lines2 = conect.browse(
            'account.move.line', move_line)
        for line in list_browse_acc_move_lines2:
            if line.account_id and line.account_id.reconcile:
                conect.write(
                    'account.move.line', line.id,
                    {'sm_id': inv_line.move_id.id})

    conect.get('account.invoice').reconcile_stock_accrual(invoice_ids)

if __name__ == '__main__':
    change_aml()