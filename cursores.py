#!/usr/bin/python
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT, ISOLATION_LEVEL_READ_COMMITTED, ISOLATION_LEVEL_REPEATABLE_READ


dbname = 'openerp_test29'
serialized = False  # True

if serialized:
    isolation_level = ISOLATION_LEVEL_REPEATABLE_READ
else:
    isolation_level = ISOLATION_LEVEL_READ_COMMITTED

# connection 1
conn = psycopg2.connect("dbname='%s'" % dbname)
conn.set_isolation_level(isolation_level)
import pdb;pdb.set_trace()
cur = conn.cursor()

SELECT_QUERY = "SELECT id, name FROM account_journal WHERE id = %s"
UPDATE_QUERY = "UPDATE account_journal SET name = 'Moy' WHERE id = %s"
journal_id = 1

cur.execute(SELECT_QUERY, (journal_id,))
print "11", cur.fetchall()

cur.execute(UPDATE_QUERY, (journal_id,))
# conn.commit()
cur.execute(SELECT_QUERY, (journal_id,))
print "12", cur.fetchall()

# connection 2
conn2 = psycopg2.connect("dbname='%s'" % dbname)
conn2.set_isolation_level(isolation_level)
cur2 = conn2.cursor()

journal_id = 2
print "29"
cur2.execute(UPDATE_QUERY, (journal_id,))
print "291"
cur2.execute(SELECT_QUERY, (journal_id,))
print "21", cur2.fetchall()
