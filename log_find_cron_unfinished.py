# pylint: disable=print-used

"""Parse a odoo.log file to search when a cron started and finished.
If started but not finished it will be detect as unfinished.

It is checking the following cron _logger.info:
 _logger.info('Starting job `%s`.', job['cron_name'])
   - https://github.com/odoo/odoo/blob/cc47c76ee70ea684ab8352c47d1d06e7d8282b1b/odoo/addons/base/models/ir_cron.py#L226
 _logger.info('Job `%s` done.', job['cron_name'])
"""


import csv
import hashlib
import os
import re
import sys
from collections import defaultdict
from datetime import datetime

DATE_PID_REGEX = re.compile(r"^(?:(?P<date>\d{4}-\d\d-\d\d \d\d:\d\d:\d\d,\d{3}) (?P<pid>\d+) )", re.M)
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S,%f"
CRON_REGEX = re.compile(
    r"(Job `(?P<cron_name_done>.*)` done)|"
    r"(Call from cron (?P<cron_name_error>.*) for server action.*)|"
    r"(Starting job `(?P<cron_name_start>.*)`\.)"
)


def lines(f_obj):
    if os.path.splitext(f_obj.name)[1].lower() == ".csv":
        # graylog export
        f_obj_csv = csv.DictReader(f_obj)
        for row in f_obj_csv:
            yield row["message"]
    else:
        yield from f_obj_csv


def get_crons_data(fname):
    crons_data = defaultdict(list)
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
                key = (cron_name, date_pid_match_dict["pid"])
                crons_data[key].append([line_date, cron_name_status, line])
    return crons_data


def main(fname):
    crons_stats = defaultdict(dict)
    crons_data = get_crons_data(fname)
    for key in crons_data:
        # Sort by date the cron events before to process
        crons_data[key].sort()
        for line_date, cron_name_status, line in crons_data[key]:
            crons_stats[key].setdefault("running", 0)
            if cron_name_status == "cron_name_start":
                crons_stats[key]["started"] = line
                crons_stats[key]["running"] += 1
                crons_stats[key]["started_datetime"] = line_date
            elif cron_name_status in ("cron_name_done", "cron_name_error"):
                crons_stats[key]["finished"] = line
                crons_stats[key]["running"] -= 1
                crons_stats[key]["finished_datetime"] = line_date

    top_heavy_crons = []
    for cron_name, step in crons_stats.items():
        if step["running"] == 0:
            diff_s = (step["finished_datetime"] - step["started_datetime"]).seconds
            if diff_s >= 30:
                top_heavy_crons.append([diff_s, cron_name, step])
                # print("cron_name: %s finisehd in %ss" % (cron_name, diff_s))
            continue
        finished = step.get("finished")
        # if finished and step['started'] <= finished:
        #     continue
        print(
            "cron_name: %s\nStarted line: %s\nFinished line: %s.\nRunnig: %d\n\n"
            % (cron_name, step["started"], finished or "", step["running"])
        )

    # print(crons)
    if top_heavy_crons:
        top_heavy_crons = sorted(top_heavy_crons, reverse=True)[:30]
        # with open("/tmp/borrar.txt", "a") as flog:
        for diff_s, cron_name, _step in top_heavy_crons:
            print("%.2fm - %s\n" % (diff_s / 60.0, cron_name))
            # flog.write("%.2fm - %s\n" % (diff_s/60.0, cron_name))


if __name__ == "__main__":
    main(sys.argv[1])
