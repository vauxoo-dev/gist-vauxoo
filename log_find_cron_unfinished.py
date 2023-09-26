# pylint: disable=print-used

"""Parse a odoo.log file to search when a cron started and finished.
If started but not finished it will be detect as unfinished.

It is checking the following cron _logger.info:
 _logger.info('Starting job `%s`.', job['cron_name'])
   - https://github.com/odoo/odoo/blob/cc47c76ee70ea684ab8352c47d1d06e7d8282b1b/odoo/addons/base/models/ir_cron.py#L226
 _logger.info('Job `%s` done.', job['cron_name'])

From graylog uses a similar filter
 - timestamp:["2023-09-25 19:26:00.000" TO "2023-09-25 19:50:04.000"] AND module:odoo.addons.base.models.ir_cron
"""

import csv
import hashlib
import os
import re
import sqlite3
import sys
from collections import defaultdict
from datetime import datetime

DATE_PID_REGEX = re.compile(r"^(?:(?P<date>\d{4}-\d\d-\d\d \d\d:\d\d:\d\d,\d{3}) (?P<pid>\d+) )", re.M)
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S,%f"
# DATETIME_FORMAT_DB = DATETIME_FORMAT.replace(",", ".")
CRON_REGEX = re.compile(
    r"(Job `(?P<cron_name_done>.*)` done)|"
    r"(Call from cron (?P<cron_name_error>.*) for server action.*)|"
    r"(Starting job `(?P<cron_name_start>.*)`\.)"
)
DB_LOG = "log.db"


def lines(f_obj):
    if os.path.splitext(f_obj.name)[1].lower() == ".csv":
        # graylog export
        f_obj_csv = csv.DictReader(f_obj)
        for row in f_obj_csv:
            yield row["message"]
    else:
        yield from f_obj_csv


def initialize_database(cr):
    cr.execute(
        """
        CREATE TABLE IF NOT EXISTS log_line (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            cron_name TEXT,
            cron_name_status TEXT,
            pid INTEGER,
            related_id INTEGER UNIQUE,
            diff_s FLOAT,
            line TEXT UNIQUE,
            FOREIGN KEY (related_id) REFERENCES log_line(id)
        )
    """
    )


def insert_crons_data(cr, fname):
    defaultdict(list)
    lines_read_sha = set()
    with open(fname) as f_obj:
        for line in lines(f_obj):
            line = line.strip(' \n"')
            cron_match = CRON_REGEX.search(line)
            if not cron_match:
                continue
            hash_obj = hashlib.new("sha1", line.encode("UTF-8"))
            line_sha = hash_obj.digest()
            if line_sha in lines_read_sha:
                continue
            lines_read_sha.add(line_sha)
            date_pid_match = DATE_PID_REGEX.search(line)
            if not date_pid_match:
                continue
            line_date = datetime.strptime(date_pid_match["date"], DATETIME_FORMAT)

            for cron_name_status, cron_name in cron_match.groupdict().items():
                if not cron_name:
                    continue
                date_pid_match_dict = date_pid_match.groupdict()
                # key = (cron_name, date_pid_match_dict["pid"])
                # crons_data[key].append([line_date, cron_name_status, line])
                cron_data = {
                    "date": line_date.strftime(DATETIME_FORMAT),
                    "pid": date_pid_match_dict["pid"],
                    "cron_name": cron_name,
                    "cron_name_status": cron_name_status.replace("cron_name_", ""),
                    "line": line,
                }
                insert_line(cr, cron_data)


def insert_line(cr, record):
    columns = ", ".join(record.keys())
    values = ", ".join(f":{key}" for key in record)
    query = f"""INSERT INTO log_line ({columns})
               VALUES ({values})
               ON CONFLICT(line) DO NOTHING
               RETURNING id
               """
    cr.execute(query, record)
    # new_id = cr.fetchone()
    # key = "Key (channel_id: %(channel_id)s, message_id: %(message_id)s)" % record
    # if new_id:
    #     _logger.info("Inserted new record id %s %s", new_id[0], key)
    # else:
    #     _logger.info("Record %s exists", key)


def match_lines(cr):
    cr.execute("SELECT * FROM log_line WHERE cron_name_status='start'")
    res = map(dict, cr.fetchall())
    for record in res:
        cr.execute(
            """
            SELECT *
            FROM log_line
            WHERE cron_name_status <> 'start'
              AND date > :date
              AND pid = :pid
            ORDER BY date ASC
            LIMIT 1
        """,
            record,
        )
        res2upd = dict(cr.fetchone())
        if not res2upd:
            continue
        date_start = datetime.strptime(record["date"], DATETIME_FORMAT)
        date_end = datetime.strptime(res2upd["date"], DATETIME_FORMAT)
        diff_time_s = (date_end - date_start).seconds
        start_id = record["id"]
        done_id = res2upd["id"]
        query = """UPDATE log_line
            SET related_id=?, diff_s=?
            WHERE id=?
        """
        cr.execute(query, (done_id, diff_time_s, start_id))
        cr.execute(query, (start_id, diff_time_s, done_id))


def print_stats(cr):
    print("unfinished")
    cr.execute("""SELECT * FROM log_line WHERE related_id IS NULL""")
    res = map(dict, cr.fetchall())
    for record in res:
        print(record)

    print("Top slow cron")
    cr.execute(
        """
        SELECT *
        FROM log_line
        WHERE cron_name_status = 'start'
        ORDER BY diff_s DESC
        LIMIT 10
    """
    )
    res = map(dict, cr.fetchall())
    for record in res:
        print(f"Cron: {record['cron_name']} pid: {record['pid']} diff_m: {round(record['diff_s']/60, 2)}")


def main(fname):
    with sqlite3.connect(DB_LOG) as conn:
        conn.isolation_level = None  # auto-commit
        conn.row_factory = sqlite3.Row  # dictfetch
        cr = conn.cursor()
        initialize_database(cr)
        insert_crons_data(cr, fname)
        match_lines(cr)
        print_stats(cr)


if __name__ == "__main__":
    main(sys.argv[1])
