from __future__ import print_function

import glob
import os
import re
import sys
from datetime import datetime

import psycopg2
import psycopg2.errorcodes

"""
odoo_log_stats_group_traceback.py   ODOO_LOG_FILE_NAME   MIN_DATE
    * ODOO_LOG_FILE_NAME path of the odoo.log file to parse
        e.g. ~/odoo.log
    * MIN_DATE format %Y-%M-%d
        e.g. 1985-04-14
"""
# SELECT l1.message, (l2.date - l1.date)  AS diff, l1.date as l1_date, l2.date AS l2_date FROM odoo_logs l1 LEFT OUTER JOIN odoo_logs l2 ON l1.id+1 = l2.id WHERE (l2.date - l1.date)  > '1 minute';
# SELECT l1.module, SUM(l2.date-l1.date) FROM odoo_logs l1 LEFT OUTER JOIN odoo_logs l2 ON l1.id+1 = l2.id GROUP BY l1.module ORDER BY SUM(l2.date-l1.date) DESC;

# Unittest running 2 times:
#  - COPY (SELECT message, COUNT(*), string_agg(module, ',') AS modules FROM odoo_logs WHERE (module ILIKE '%test%' OR message ILIKE '%test%') AND db='openerp_test' GROUP BY message HAVING count(*)>1 ORDER BY message) to '/tmp/borrar.csv' WITH CSV HEADER;

# Unittest spending most time
# - SELECT CAST(SUBSTRING(message FROM ' (\d+\.\d+)s') AS FLOAT) AS seconds, module FROM odoo_logs WHERE message ILIKE 'Ran %' ORDER BY 1 DESC;

DBNAME = 'odoologs'
try:
    MIN_DATE = sys.argv[2]
except IndexError:
    MIN_DATE = None

FILE_NAME = os.path.expandvars(os.path.expanduser(sys.argv[1]))

# Parsing the following logger message output
# https://github.com/odoo/odoo/blob/3da37bb2474318463a40deba2878a83102c37984/odoo/netsvc.py#L135
# TODO: Support ctime part  ,\d{3}
_re_log = r'(?P<date>^\d{4}-\d\d-\d\d \d\d:\d\d:\d\d),\d{3} (?P<session>\d+) (?P<level>WARNING|ERROR|INFO|DEBUG) (?P<db>[0-9a-zA-Z$_\?\-\_]+) (?P<module>[0-9a-zA-Z$_\.]+): (?P<message>.*)'
_re_poll_log = r' (?P<date>\[\d{4}-\d\d-\d\d \d\d:\d\d:\d\d\]|\[\d\d\/[A-Z][a-z][a-z]\/\d{4} \d\d:\d\d:\d\d\]) '
insert_query = (
    "INSERT INTO odoo_logs (date, session, db, level, module, message) "
    "VALUES (%(date)s, %(session)s, %(db)s, %(level)s, %(module)s, %(message)s)")


def init_db():
    cr.execute("""
        CREATE TABLE IF NOT EXISTS odoo_logs (
            id serial NOT NULL, PRIMARY KEY(id),
            date timestamp without time zone,
            session integer,
            db varchar(64),
            level varchar(64),
            module text,
            logger_name text,
            message text
    );""")
    cr.execute("""CREATE INDEX IF NOT EXISTS odoo_logs_level ON odoo_logs (level);""")
    cr.execute("""CREATE UNIQUE INDEX IF NOT EXISTS odoo_logs_unique_date_level_message ON odoo_logs (date, level, md5(message), module, session, db);""")
    conn.commit()


def get_message_split(message_str):
    # Remove colors
    message_str = message_str.replace("\x1b[1;32m\x1b[1;49m", "")
    message_str = message_str.replace("\x1b[0m", "")
    # message_str = message_str.replace("[0m ", "")
    match = re.match(_re_log, message_str)
    if not match:
        return {}
    return match.groupdict()


def insert_message(message):
    if MIN_DATE and MIN_DATE >= datetime.strptime(message['date'], '%c'):
        return
    message['date'] = message['date']
    cr.execute("SAVEPOINT msg")
    try:
        cr.execute(insert_query, message)
    except psycopg2.IntegrityError as ie:
        if ie.pgcode == psycopg2.errorcodes.UNIQUE_VIOLATION:
            print("Bypass repeated logs:", str(ie))
            cr.execute("ROLLBACK TO SAVEPOINT msg")
        # raise ie
    except psycopg2.DataError as de:
        print("Data error %s:\nQuery: %s" % (de, cr.query))
    else:
        cr.execute("RELEASE SAVEPOINT msg")
    conn.commit()


def insert_messages(filename):
    with open(filename) as fp:
        message = {}
        message_items = []
        for line in fp:
            message_items = get_message_split(line)
            if any(map(lambda item: item in line, [' WARNING ', ' ERROR ', ' INFO ', ' DEBUG '])) and not message_items:
                print("Log has a message not supported\n%s\n%s" % (line, _re_log))
            if not message_items:
                if re.findall(_re_poll_log, line):
                    # TODO: Check if the longpoll logger is not overwritten the original one
                    continue
                if message:
                    message['message'] += "\n" + line.strip()
                continue
            elif message:
                # yield message
                insert_message(message)
            message = message_items
            message['message'] = message['message'].strip()
        if message and message != message_items:
            message['logger_name'] = message['module']
            message['module'] = message['module'].split('.')[0]
            insert_message(message)
        # conn.commit()


try:
    conn = psycopg2.connect(dbname=DBNAME)
except psycopg2.OperationalError as op_err:
    print("Run: createdb -T template0 -E unicode --lc-collate=C %s" % DBNAME)
    print("Create a postgresql rol for the OS user and "
          "assign global environment variable to connect if it is different to default")
    raise op_err

try:
    cr = conn.cursor()
    init_db()
    for filename in glob.glob(FILE_NAME):
        insert_messages(filename)
finally:
    conn.close()
# After you can get common messages running:
# psql odoologs_mod -c "SELECT count(*) AS count, message FROM odoo_logs WHERE level = 'WARNING' AND message ILIKE '%cache%' GROUP BY message ORDER BY count(*) DESC;" >mod_odoo_logs_warning_cache.txt
