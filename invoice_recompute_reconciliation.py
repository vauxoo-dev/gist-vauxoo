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
def recompute_invoice(po, dbo, uo, pod):

    time_start = time.ctime()

    conect = oerplib.OERP('localhost', port=pod, timeout=7200)
    conect.login(user=uo, passwd=po, database=dbo)

    invoice_ids = conect.search('account.invoice', [
        ('type', 'in', ('in_invoice', 'out_invoice')),
        ('residual', '=', 0),
        ('state', '=', 'open'),
        ])

    if not invoice_ids:
        print "No invoice to reconcile"
        return True

    invoice_brws = conect.browse('account.invoice', invoice_ids)

    for inv_brw in invoice_brws:
        if not inv_brw.move_id:
            print "Invoice without move_id {ids}".format(ids=inv_brw.id)
            continue
        ttype = 'receivable' if inv_brw.type == 'out_invoice' else 'payable'
        account_id = [aml_brw.account_id.id
                      for aml_brw in inv_brw.move_id.line_id
                      if aml_brw.account_id.type == ttype]
        if not account_id:
            print "Invoice without account {ids}".format(ids=inv_brw.id)
            continue
        print "Invoice writing account on {ids}".format(ids=inv_brw.id)
        conect.write('account.invoice', inv_brw.id, {'account_id': account_id[0]})

    print "Finished At all"

    time_stop = time.ctime()
    print time_start
    print time_stop

    return True

if __name__ == '__main__':
    recompute_invoice()
