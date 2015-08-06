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

for invoice in con.browse('account.invoice', invoice_ids):
    name_invoice = invoice.name
    con.write('account.invoice', invoice.id, {'name': ' '})
    con.write('account.invoice', invoice.id, {'name': name_invoice})
