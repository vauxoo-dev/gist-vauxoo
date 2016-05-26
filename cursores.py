import psycopg2
conn = psycopg2.connect("dbname='omlLuis5'")
conn2 = psycopg2.connect("dbname='omlLuis5'")
cur = conn.cursor()
print id(cur)
cur.execute('SELECT id, name FROM account_journal;')
print cur.fetchall()

cur2 = conn2.cursor()
print id(cur2)

cur.execute("UPDATE account_journal SET name = 'Moy' WHERE id = 1;")
print dir(cur)
conn.commit()
cur.execute('SELECT id, name FROM account_journal;')
print cur.fetchall()

cur2.execute('SELECT id, name FROM account_journal;')
print cur2.fetchall()
