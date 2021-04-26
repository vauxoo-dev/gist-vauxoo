# ~/instance/odoo/odoo-bin shell -d DB --no-http < ~/backups_db_dev/islamic_migration/get_bad_domain.py

import psycopg2
from odoo.tools import mute_logger


cr = env.cr
cr.execute("SELECT table_name, column_name FROM information_schema.columns WHERE column_name ILIKE '%domain%';")
res = cr.dictfetchall()
for r in res:
    if r['column_name'] == 'show_domain':
        continue
    try:
        with cr.savepoint(), mute_logger('odoo.sql_db'):
            cr.execute("SELECT id, REPLACE(TRIM(%(column_name)s), '\t', '') FROM %(table_name)s WHERE %(column_name)s ILIKE '%%’%%' OR REPLACE(TRIM(%(column_name)s), '\t', '') NOT ILIKE '\\[%%\\]'" % r)
            wrongs = cr.dictfetchall()
    except psycopg2.ProgrammingError as e:
        continue
    if wrongs:
        print(r)
    for wrong in wrongs:
        print(wrong)
print("finished!")
