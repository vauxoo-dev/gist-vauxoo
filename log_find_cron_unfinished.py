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
import os
import re
import sqlite3
import sys
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
    cr.execute("CREATE INDEX IF NOT EXISTS log_line_cron_name_date_pid_idx ON log_line (cron_name, date, pid)")


def insert_crons_data(cr, fname):
    with open(fname) as f_obj:
        for line in lines(f_obj):
            line = line.strip(' \n"')
            cron_match = CRON_REGEX.search(line)
            date_pid_match = DATE_PID_REGEX.search(line)
            if not cron_match or not date_pid_match:
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
    cr.execute("SELECT * FROM log_line WHERE cron_name_status='start' ORDER BY date ASC")
    res = map(dict, cr.fetchall())
    for record in res:
        # query = """SELECT l1.id AS start_id, l2.id AS end_id
        # FROM log_line AS l1
        # LEFT JOIN log_line AS l2 ON l2.id = (
        #     SELECT l3.id
        #     FROM log_line AS l3
        #     WHERE l3.cron_name_status <> 'start'
        #         AND l3.date > l1.date
        #         AND l3.pid = l1.pid
        #         AND l3.cron_name = l1.cron_name
        #     ORDER BY l3.date ASC
        #     LIMIT 1)
        # WHERE l1.cron_name_status = 'start'
        # AND l1.id <> l2.related_id
        # ORDER BY l1.date ASC
        # """

        cr.execute(
            """
            SELECT *
            FROM log_line
            WHERE cron_name_status <> 'start'
              AND date > :date
              AND pid = :pid
              AND cron_name = :cron_name
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

        # Clean old related_id in order to only store the most recent and closest
        query = """UPDATE log_line
            SET related_id=Null, diff_s=Null
            WHERE related_id IN (?, ?)
        """
        cr.execute(query, (start_id, done_id))

        query = """UPDATE log_line
            SET related_id=?, diff_s=?
            WHERE id=?
        """
        cr.execute(query, (done_id, diff_time_s, start_id))
        cr.execute(query, (start_id, diff_time_s, done_id))


def print_stats(cr):
    cr.execute("""SELECT max(date), min(date) FROM log_line""")
    max_min = dict(cr.fetchone())
    print(max_min)
    print("==== Unfinished ====")
    cr.execute(
        """SELECT *
        FROM log_line
        WHERE related_id IS NULL
          AND cron_name_status = 'start'
        ORDER BY date"""
    )
    res = map(dict, cr.fetchall())
    for record in res:
        print(record)

    print("==== Top slow cron ====")
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
        print(
            f"Cron: {record['cron_name']} pid: {record['pid']} diff_m: {round(record['diff_s']/60, 2)}"
            f"\nline: {record['line']}\n"
        )


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
