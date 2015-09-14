#!/usr/bin/python
import oerplib
import os
import sys

HOST= ''
PORT= 
DB= ''
USER= ''
PASS= ''

con = oerplib.OERP(
server=HOST,
database=DB,
port=PORT,
)

con.login(USER, PASS)

invoice_ids = con.search('account.invoice', [])
invoice_error = []
for invoice in con.browse('account.invoice', invoice_ids):
    invoice_number = invoice.id
    try:
        name_invoice = invoice.name
        con.write('account.invoice', invoice.id, {'name': ' '})
        con.write('account.invoice', invoice.id, {'name': name_invoice})
    except Exception:
        invoice_error.append(invoice_number)
if invoice_error:
    print "This invoice has a error: "
    print invoice_error
else:
    print 'No errors'
