import glob
import json
import os
import re
import sys
from datetime import datetime

import psycopg2
import psycopg2.errorcodes

try:
    import geoip2.database
    import geoip2.errors
except ImportError:
    print("Requires 'pip install geoip2==4.5.0' to get ip info")

geoip_default_paths = [
    "/usr/share/GeoIP/GeoLite2-City.mmdb",
    "/usr/local/share/GeoIP/GeoLite2-City.mmdb",
]
geoip_path = None
for geoip_default_path in geoip_default_paths:
    if os.path.isfile(geoip_default_path):
        geoip_path = geoip_default_path

if not geoip_path:
    print(
        """Requires download geoip database
GEOIP2_URLS="https://s3.vauxoo.com/GeoLite2-City_20191224.tar.gz https://s3.vauxoo.com/GeoLite2-Country_20191224.tar.gz https://s3.vauxoo.com/GeoLite2-ASN_20191224.tar.gz"
GEOIP_PATH="/usr/local/share/GeoIP"
function geoip_install(){
    URLS="${1}"
    DIR="$( mktemp -d )"
    mkdir -p $GEOIP_PATH
    for URL in ${URLS}; do
        wget -qO- "${URL}" | tar -xz -C "${DIR}/"
        mv "$(find ${DIR} -name "GeoLite2*mmdb")" "$GEOIP_PATH"
    done
    rm -rf "${DIR}"
}
geoip_install "${GEOIP2_URLS}"
    """
    )

"""
odoo_log_stats_group_traceback.py   ODOO_LOG_FILE_NAME   MIN_DATE
    * ODOO_LOG_FILE_NAME path of the odoo.log file to parse
        e.g. ~/odoo.log
    * MIN_DATE format %Y-%M-%d
        e.g. 1985-04-14
"""
# SELECT l1.message, (l2.date - l1.date)  AS diff, l1.date as l1_date, l2.date AS l2_date FROM odoo_logs l1 LEFT OUTER JOIN odoo_logs l2 ON l1.id+1 = l2.id WHERE (l2.date - l1.date)  > '1 minute';
# SELECT l1.module, SUM(l2.date-l1.date) FROM odoo_logs l1 LEFT OUTER JOIN odoo_logs l2 ON l1.id+1 = l2.id GROUP BY l1.module ORDER BY SUM(l2.date-l1.date) DESC;

# Unittest running 2 times:
#  - COPY (SELECT message, COUNT(*), string_agg(module, ',') AS modules FROM odoo_logs WHERE (module ILIKE '%test%' OR message ILIKE '%test%') AND db='openerp_test' GROUP BY message HAVING count(*)>1 ORDER BY message) to '/tmp/borrar.csv' WITH CSV HEADER;

# Unittest spending most time
# - SELECT CAST(SUBSTRING(message FROM ' (\d+\.\d+)s') AS FLOAT) AS seconds, module FROM odoo_logs WHERE message ILIKE 'Ran %' ORDER BY 1 DESC;

# Loading file spending most time
# - SELECT module, diff, message, db FROM (SELECT (l2.date - l1.date)  AS diff, l1.date as l1_date, l2.date AS l2_date,  l1.* FROM odoo_logs l1 LEFT OUTER JOIN odoo_logs l2 ON l1.id+1 = l2.id) vw WHERE module = 'odoo.modules.loading' ORDER BY 2 DESC;

# Unittest spending most time v2
# CREATE VIEW odoo_logs_test AS (SELECT row_number() OVER() AS row_number, * FROM odoo_logs WHERE module LIKE '%\.tests\.%' AND (message LIKE 'test\_%' OR message LIKE 'Ran %') ORDER BY id);
# SELECT module, diff, message, db FROM (SELECT (l2.date - l1.date)  AS diff, l1.date as l1_date, l2.date AS l2_date,  l1.* FROM odoo_logs_test l1 LEFT OUTER JOIN odoo_logs_test l2 ON l1.row_number+1 = l2.row_number ORDER BY id) vw WHERE message LIKE 'test\_%' ORDER BY 2 DESC;

# SELECT * FROM (SELECT count(*), DATE_TRUNC('minute', date) AS minute_timestamp FROM odoo_logs GROUP BY DATE_TRUNC('minute', date) ORDER BY 1 DESC LIMIT 30) order by 2;
# SELECT message, ip_data->'country'->>'iso_code' FROM odoo_logs WHERE date BETWEEN '2024-04-22 15:11:00' AND '2024-04-22 16:12:00';


DBNAME = "odoologs"
try:
    MIN_DATE = sys.argv[2]
except IndexError:
    MIN_DATE = None

FILE_NAME = os.path.expandvars(os.path.expanduser(sys.argv[1]))

# Parsing the following logger message output
# https://github.com/odoo/odoo/blob/3da37bb2474318463a40deba2878a83102c37984/odoo/netsvc.py#L135
# TODO: Support ctime part  ,\d{3}
_re_log = r"(?P<date>^\d{4}-\d\d-\d\d \d\d:\d\d:\d\d,\d{3}) (?P<pid>\d+) (?P<level>WARNING|ERROR|INFO|DEBUG) (?P<db>[0-9a-zA-Z$_\?\-\_]+) (?P<module>[0-9a-zA-Z$_\.]+): (?P<message>.*)"
_re_poll_log = r" (?P<date>\[\d{4}-\d\d-\d\d \d\d:\d\d:\d\d\]|\[\d\d\/[A-Z][a-z][a-z]\/\d{4} \d\d:\d\d:\d\d\]) "
_re_ip_compile = re.compile(r"^(?P<ip>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})|(([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4})) ")
_re_werkzeug_log_compile = re.compile(
    r"\"(?P<action>(POST|GET)) (?P<url>.*) HTTP.* (?P<response>\d\d\d) \- \d+ (?P<time1>\d+.\d+) (?P<time2>\d+.\d+)"
)

insert_query = (
    "INSERT INTO odoo_logs (date, pid, db, level, module, message, ip, action, url, response, time1, time2, ip_data) "
    "VALUES (%(date)s, %(pid)s, %(db)s, %(level)s, %(module)s, %(message)s, %(ip)s, %(action)s, %(url)s, %(response)s, %(time1)s, %(time2)s, %(ip_data)s)"
)


def init_db(cr, conn):
    cr.execute(
        """
        CREATE TABLE IF NOT EXISTS odoo_logs (
            id serial NOT NULL, PRIMARY KEY(id),
            date timestamp without time zone,
            pid integer,
            db varchar(64),
            level varchar(64),
            module text,
            logger_name text,
            message text,
            ip text,
            action text,
            url text,
            response integer,
            time1 float,
            time2 float,
            ip_data jsonb
    );"""
    )
    cr.execute("""CREATE INDEX IF NOT EXISTS odoo_logs_level ON odoo_logs (level);""")
    cr.execute(
        """CREATE UNIQUE INDEX IF NOT EXISTS odoo_logs_unique_date_level_message ON odoo_logs (date, level, md5(message), module, pid, db);"""
    )
    conn.commit()


def get_message_split(message_str):
    # Remove colors
    message_str = message_str.replace("\x1b[1;32m\x1b[1;49m", "")
    message_str = message_str.replace("\x1b[0m", "")
    # message_str = message_str.replace("[0m ", "")
    match = re.match(_re_log, message_str)
    if not match:
        return {}
    message_data = match.groupdict()
    # ms format valid for postgresql using . instead of ,
    message_data["date"] = message_data["date"].replace(",", ".", 1)
    return message_data


def get_message_details(message):
    """Get IP from message"""
    new_data = dict.fromkeys(set(_re_ip_compile.groupindex.keys()) | set(_re_werkzeug_log_compile.groupindex.keys()))
    new_data.update({"ip_data": None})
    ip_match = _re_ip_compile.match(message)
    if ip_match:
        new_data.update(ip_match.groupdict())
        ip = new_data["ip"]
        geoipdb = geoip2.database.Reader(geoip_path)
        try:
            ip_json = json.dumps(geoipdb.city(ip).raw)
            new_data["ip_data"] = ip_json
        except geoip2.errors.AddressNotFoundError:
            # Local IPs
            pass

    werkzeug_match = _re_werkzeug_log_compile.search(message)
    if werkzeug_match:
        new_data.update(werkzeug_match.groupdict())
    return new_data


def insert_message(message, cr, conn):
    if MIN_DATE and MIN_DATE >= datetime.strptime(message["date"], "%c"):
        return
    # message['date'] = message['date']
    message.update(get_message_details(message["message"]))
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


def insert_messages(filename, cr, conn):
    with open(filename) as fp:
        message = {}
        message_items = []
        for line in fp:
            message_items = get_message_split(line)
            if (
                any(map(lambda item: item in line, [" WARNING ", " ERROR ", " INFO ", " DEBUG "]))
                and not message_items
            ):
                print("Log has a message not supported\n%s\n%s" % (line, _re_log))
            if not message_items:
                if re.findall(_re_poll_log, line):
                    # TODO: Check if the longpoll logger is not overwritten the original one
                    continue
                if message:
                    message["message"] += "\n" + line.strip()
                continue
            if message:
                # yield message
                insert_message(message, cr, conn)
            message = message_items
            message["message"] = message["message"].strip()
        if message and message != message_items:
            message["logger_name"] = message["module"]
            message["module"] = message["module"].split(".")[0]
            insert_message(message, cr, conn)
        # conn.commit()


def main():
    try:
        conn = psycopg2.connect(dbname=DBNAME)
    except psycopg2.OperationalError as op_err:
        print("Run: createdb -T template0 -E unicode --lc-collate=C %s" % DBNAME)
        print(
            "Create a postgresql rol for the OS user and "
            "assign global environment variable to connect if it is different to default"
        )
        raise op_err

    try:
        cr = conn.cursor()
        init_db(cr, conn)
        for filename in glob.glob(FILE_NAME):
            insert_messages(filename, cr, conn)
    finally:
        conn.close()
    # After you can get common messages running:
    # psql odoologs_mod -c "SELECT count(*) AS count, message FROM odoo_logs WHERE level = 'WARNING' AND message ILIKE '%cache%' GROUP BY message ORDER BY count(*) DESC;" >mod_odoo_logs_warning_cache.txt


if __name__ == "__main__":
    main()
