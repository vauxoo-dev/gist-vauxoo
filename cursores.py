#!/usr/bin/python

"""
Case of use to known the ISOLATION_LEVEL_REPEATABLE_READ database psycopg way
The output of this script was:
 cursor 1 - select to add cache with ISOLATION_LEVEL_REPEATABLE_READ
 [(1, 'Sales Journal - (test)')]
 cursor 2 - select to add cache with ISOLATION_LEVEL_REPEATABLE_READ
 [(1, 'Sales Journal - (test)')]
 cursor 1 - update row and commit
 cursor 1 - read again (updated cache) [(1, 'Moy')]
 cursor 2 - read again (outdated cache) [(1, 'Sales Journal - (test)')]

FYI odoo use ISOLATION_LEVEL_REPEATABLE_READ more info here:
https://github.com/odoo/odoo/blob/b08642c21cb345aa0778bdc9754425eb9ac9faa7/openerp/sql_db.py#L69-L128

I fixed this issue using the following changes:
https://github.com/Vauxoo/odoo-mexico-v2/pull/340/files
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_REPEATABLE_READ


# ISOLATION_LEVEL_REPEATABLE_READ:
#   use cache to avoid read the database by each time
def create_connection(dbname, isolation_level=ISOLATION_LEVEL_REPEATABLE_READ):
    conn = psycopg2.connect("dbname='%s'" % dbname)
    conn.set_isolation_level(isolation_level)
    cur = conn.cursor()
    return conn, cur


dbname = 'openerp_test29'
conn1, cur1 = create_connection(dbname)
conn2, cur2 = create_connection(dbname)
SELECT_QUERY = "SELECT id, name FROM account_journal WHERE id = %s"
UPDATE_QUERY = "UPDATE account_journal SET name = 'Moy' WHERE id = %s"
row_id = 1

cur1.execute(SELECT_QUERY, (row_id,))
print "cursor 1 - select to add cache with ISOLATION_LEVEL_REPEATABLE_READ"
print cur1.fetchall()

cur2.execute(SELECT_QUERY, (row_id,))
print "cursor 2 - select to add cache with ISOLATION_LEVEL_REPEATABLE_READ"
print cur2.fetchall()

cur1.execute(UPDATE_QUERY, (row_id,))
conn1.commit()
print "cursor 1 - update row and commit"

cur1.execute(SELECT_QUERY, (row_id,))
print "cursor 1 - read again (updated cache)", cur1.fetchall()

cur2.execute(SELECT_QUERY, (row_id,))
print "cursor 2 - read again (outdated cache)", cur2.fetchall()

