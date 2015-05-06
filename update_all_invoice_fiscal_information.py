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
    comment_currently = invoice.comment
    con.write('account.invoice', invoice.id, {'comment': ' '})
    con.write('account.invoice', invoice.id, {'comment': comment_currently})
