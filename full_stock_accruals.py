# !/usr/bin/env python
# -*- coding: utf-8 -*-
import oerplib
import logging
import datetime
import click
import time

# import psycopg2
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
@click.option('-upsm', default=0, prompt='Update Stock Move AML [0/1]',
              help='Update Stock Move AML')
@click.option('-upil', default=0, prompt='Update Invoice Lines AML [0/1]',
              help='Update Invoice Lines AML')
@click.option('-rc', default=0, prompt='Reconcile Stock & Invoice [0/1]',
              help='Reconcile Stock & Invoice AML')
@click.option('-test', default=1, prompt='Test Script, No Writes [0/1]',
              help='Perform only a test, Do not execute writes on DB')
def change_aml(po, dbo, uo, pod, du, dp, dpo, dh, fini, ffin, upsm, upil, rc,
               test):

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

    conect = oerplib.OERP('localhost', port=pod, timeout=7200)
    conect.login(user=uo, passwd=po, database=dbo)
    account_period_obj = conect.get('account.period')
    ffin = datetime.datetime.strptime(ffin, '%d/%m/%Y').strftime('%m/%d/%Y')
    fini = datetime.datetime.strptime(fini, '%d/%m/%Y').strftime('%m/%d/%Y')

    if upsm:
        product_ids = conect.search(
            'product.product', [('valuation', '=', 'real_time')])
        move_ids = conect.search(
            'stock.move', [
                ('product_id', 'in', product_ids),
                ('picking_id', '!=', False),
                ('state', '=', 'done'),
                ('picking_type_id.code', '=', 'outgoing'),
                ('date', '>=', fini),
                ('date', '<=', ffin)])
        pick_ids = {}

        reads = conect.read(
            'stock.move', move_ids, ['id', 'date', 'picking_id', 'product_id'])
        total = len(reads)
        move_count = 0
        for move in reads:
            move_id, product_id = move.get('id'), move.get('product_id')[0]

            move_count += 1
            print "Stock Reading [{count} / {total}]".format(
                total=total, count=move_count)

            if (move_id, product_id) in pick_ids.keys():
                print "Picking already checked"
                continue
            else:
                pick_ids[(move_id, product_id)] = True
            date_move = datetime.datetime.strptime(
                str(move.get('date')), '%Y-%m-%d %H:%M:%S').date().strftime(
                '%Y-%m-%d')
            # save this period this way we do not waste time searching several
            # times for the same resource
            # by using memoize technique
            period_id = find_period(account_period_obj, date_move)
            if not period_id:
                print "No period found"
                continue

            aml_ids = conect.search(
                'account.move.line', [
                    ('ref', '=', move.get('picking_id')[1]),
                    ('product_id', '=', product_id),
                    ('period_id', '=', period_id),
                    ('account_id.reconcile', '=', True),
                ])

            if not aml_ids:
                # We continue with next move, there nothing to do here
                print "No Journal Items to update"
                continue

            print "Writing on {count} Entry Lines for Stock Move".format(
                count=len(aml_ids))
            if not test:
                conect.write(
                    "account.move.line", aml_ids,
                    {'sm_id': move.get("id")})
            print "Finished writing on Journal Entry Lines"

    if upil or rc:
        invoice_ids = conect.search('account.invoice', [
            ('date_invoice', '>=', fini),
            ('date_invoice', '<=', ffin),
            ('type', '=', 'out_invoice'),
            ('state', 'not in', ('cancel', 'draft')),
            ])

        if not invoice_ids:
            return True

    if upil:
        inv_reads = conect.read(
            'account.invoice', invoice_ids, ['id', 'move_id'])

        count_ai = 0
        total_ai = len(inv_reads)
        ail_moves = {}

        for inv_dict in inv_reads:
            count_ai += 1

            invoice_line = conect.search(
                'account.invoice.line',
                [('invoice_id', '=', inv_dict['id']),
                 ('move_id', '<>', False)])
            ail_reads = conect.read(
                'account.invoice.line', invoice_line,
                ['id', 'product_id', 'quantity', 'move_id'])
            total_ail = len(ail_reads)
            count_ail = 0
            for ail_dic in ail_reads:
                count_ail += 1
                print (
                    "Invoice Reading [{count} / {total}] [{count_ail} /"
                    " {total_ail}]").format(
                    total=total_ai,
                    count=count_ai,
                    total_ail=total_ail,
                    count_ail=count_ail,
                    )
                move_line = conect.search('account.move.line', [
                    ('product_id', '=', ail_dic['product_id'][0]),
                    ('move_id', '=', inv_dict['move_id'][0]),
                    ('quantity', '=', ail_dic['quantity']),
                    ('account_id.reconcile', '=', True),
                    ])
                if not move_line:
                    continue

                if ail_moves.get(ail_dic['move_id'][0]):
                    ail_moves[ail_dic['move_id'][0]] += move_line
                else:
                    ail_moves[ail_dic['move_id'][0]] = move_line

        if not ail_moves:
            print "No Invoice Lines to update"

        totalsm = len(ail_moves)
        countsm = 0
        for sm_id, aml_idss in ail_moves.iteritems():
            countsm += 1
            print "Writing Stock on AML for AIL [{count} / {total}]".format(
                count=countsm,
                total=totalsm,
            )

            if not test:
                conect.write(
                    'account.move.line', aml_idss,
                    {'sm_id': sm_id})

    if rc:
        print "Reconciling Invoices"

        countai = 0
        totalai = len(invoice_ids)

        for inv_id in invoice_ids:
            countai += 1
            print "Reconciling Invoice [{count} / {total}] id {inv_id}".format(
                total=totalai,
                count=countai,
                inv_id=inv_id
            )
            try:
                if not test:
                    conect.get('account.invoice').reconcile_stock_accrual(
                        [inv_id])
                print "Reconciled Done"
            except:
                print "Already reconciled"
    print "Finished At all"

    time_stop = time.ctime()
    print time_start
    print time_stop

    return True

if __name__ == '__main__':
    change_aml()
