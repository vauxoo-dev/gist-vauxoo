# !/usr/bin/env python
# -*- coding: utf-8 -*-
import oerplib
import logging
import datetime
import click
import time

import psycopg2
import functools
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


def change_aml(po, dbo, uo, pod, du, dp, dpo, dh, fini, ffin):
    time_start = time.ctime()
    def memoize(func):
        """
        Pro python Marty Alchin, Pag  75, Memoization
        """
        cache = {}

        @functools.wraps(func)
        def wrapper(*args):
            if args in cache:
                # print "return cached value"
                return cache[args]
            result = func(*args)
            cache[args] = result
            # print "return value from DB"
            return result
        return wrapper

    @memoize
    def find_period(obj, date, context=None):
        period_id = obj.find(dt=date, context=context)
        return period_id and period_id[0] or False

    @memoize
    def browse_period_state(obj, ids, context=None):
        return obj.browse(ids).state

    conect = oerplib.OERP('localhost', port=pod)
    conect.login(user=uo, passwd=po, database=dbo)
    account_period_obj = conect.get('account.period')
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

    # file_new = open('/tmp/moves_changeds.csv', 'wb')
    # file_new.write('id, name, date, period\n')

    # Open a new period variable so that:
    # it can be remember the last state of the period and the revert it back to
    # its previous state
    period_restore = {}
    reads = conect.read('stock.move', move_ids, ['id', 'date', 'picking_id'])
    total = len(reads)
    move_count = 0
    for move in reads:

        move_count += 1
        print "[{count} / {total}]".format(total=total, count=move_count)

        if move.get('picking_id')[0] in pick_ids:
            print "Picking already checked"
            continue
        else:
            pick_ids.append(move.get('picking_id')[0])
        date_move = datetime.datetime.strptime(
            str(move.get('date')), '%Y-%m-%d %H:%M:%S').date().strftime(
            '%Y-%m-%d')
        # save this period this way we do not waste time searching several
        # times for the same resource
        # by using memoize technique
        period_id = find_period(account_period_obj, date_move)
        if not period_id:
            continue

        period_state = browse_period_state(account_period_obj, period_id)

        acc_m_ids = conect.search(
            'account.move', [
                ('ref', '=', move.get('picking_id')[1]),
                ('period_id', '=', period_id)
            ])

        if not acc_m_ids:
            # We continue with next move, there nothing to do here
            print "No Journal Entries"
            continue

        # we can save a lot of time by only opening once this record and after
        # finishing it we set it back to its previous state
        if period_state == "done" and not period_restore.get(period_id):
            account_period_obj.action_draft([period_id])
            period_restore[period_id] = period_state

        count_am = 0
        am_brws = conect.browse('account.move', acc_m_ids)
        total_am = len(am_brws)
        aml_ids = []
        for acc_mv in am_brws:
            count_am += 1
            print "[{count} / {total}] [{count_am} / {total_am}] Reading Journal Entry {name}".format(
                    count=move_count,
                    total=total,
                    count_am=count_am,
                    total_am=total_am,
                    name=acc_mv.name,
                    )
            # TODO: Optimize this is being done on all lines regardless
            # reconcilable

            aml_ids += acc_mv.line_id.ids

            # aml_ids += [aml_brw.id for aml_brw in acc_mv.line_id
            #            if aml_brw.account_id.reconcile]
        if not aml_ids:
            print "No Journal Items to update"
            continue
        conect.write(
            "account.move.line", aml_ids,
            {'sm_id': move.get("id")})
        print "Finished writing on Journal Entry Lines"

        # file_new.write(
        #     '%s, %s\n' % (
        #         str(aml_ids), str(move.get("id")) or ''))

    # This process is to be done out the for loop to avoid wasting resource
    # opening and closing same period several time
    if period_restore:
        print "Restoring Period States"
    else:
        print "No Periods to Restore"

    for pid in period_restore.keys():
        print "State id: {pid} restored".format(pid=pid)
        wizard_period_close_id = conect.create(
            'account.period.close', {'sure': 1})
        conect.execute(
            'account.period.close', 'data_save',
            [wizard_period_close_id], {
                'lang': 'en_US',
                'active_model': 'account.period',
                'active_ids': [pid],
                'tz': False,
                'active_id': [pid]
            }
        )

    # file_new.close()

    time_stop = time.ctime()
    print time_start
    print time_stop

    return True

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
