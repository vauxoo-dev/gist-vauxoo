from __future__ import print_function

import glob
import re
import psycopg2


DBNAME = 'odoologs_moi'

# FILE_NAME = "/home/odoo/production_logs/20181208/Logs 20181208/MoD_Odoo_log/odoo-server.log*"
FILE_NAME = "/home/odoo/production_logs/20181208/Logs 20181208/MoI_Odoo_log/odoo-server.log"
_re_log = r'(?P<date>^\d{4}-\d\d-\d\d \d\d:\d\d:\d\d),\d{3} (?P<session>\d+) (?P<level>WARNING|ERROR|INFO|DEBUG) (?P<db>[0-9a-zA-Z$_]+) (?P<module>[0-9a-zA-Z$_\.]+): (?P<message>.*)'
_re_poll_log = r' (?P<date>\[\d{4}-\d\d-\d\d \d\d:\d\d:\d\d\]|\[\d\d\/[A-Z][a-z][a-z]\/\d{4} \d\d:\d\d:\d\d\]) '
insert_query = (
    "INSERT INTO odoo_logs (date, session, db, level, module, message) "
    "VALUES (%(date)s, %(session)s, %(db)s, %(level)s, %(module)s, %(message)s)")


def init_db():
    cr.execute("""
        CREATE TABLE IF NOT EXISTS odoo_logs (
            id serial NOT NULL,
            date timestamp without time zone,
            session integer,
            db varchar(64),
            level varchar(64),
            module varchar(64),
            message varchar
    );""")
    cr.execute("""CREATE INDEX IF NOT EXISTS odoo_logs_message ON odoo_logs (message);""")
    cr.execute("""CREATE INDEX IF NOT EXISTS odoo_logs_level ON odoo_logs (level);""")
    cr.execute("""CREATE INDEX IF NOT EXISTS odoo_logs_level_message ON odoo_logs (level, message);""")
    conn.commit()


def get_message_split(message_str):
    match = re.match(_re_log, message_str)
    if not match:
        return {}
    return match.groupdict()


def insert_messages(filename):
    with open(filename) as fp:
        message = {}
        for line in fp:
            message_items = get_message_split(line)
            if not message_items:
                if re.findall(_re_poll_log, line):
                    # TODO: Check if the longpoll logger is not overwritten the original one
                    continue
                if message:
                    message['message'] += line
                continue
            message = message_items
            cr.execute(insert_query, message)
        if message and message != message_items:
            cr.execute(insert_query, message)
        conn.commit()


try:
    conn = psycopg2.connect(dbname=DBNAME)
except psycopg2.OperationalError as op_err:
    print("Run: createdb -T template0 -E unicode --lc-collate=C %s" % DBNAME)
    print("Create a postgresql rol for the OS user and "
          "assign global environment variable to connect if it are different to default")
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