"""
Parse a odoo.log file to search when a cron started and finished.
If started but not finished it will be detect as unfinished.

It is checking the following cron _logger.info:
 _logger.info('Starting job `%s`.', job['cron_name'])
   - https://github.com/odoo/odoo/blob/cc47c76ee70ea684ab8352c47d1d06e7d8282b1b/odoo/addons/base/models/ir_cron.py#L226
 _logger.info('Job `%s` done.', job['cron_name'])
"""


import csv
import os
import re
import sys
from collections import defaultdict
from datetime import datetime

date_pid_regex = re.compile(r"^(?:(\d{4}-\d\d-\d\d \d\d:\d\d:\d\d,\d{3}) (\d+) )", re.M)
datetime_format = "%Y-%m-%d %H:%M:%S,%f"


def lines(f_obj):
    if os.path.splitext(f_obj.name)[1].lower() == ".csv":
        # graylog export
        f_obj_csv = csv.DictReader(f_obj)
        for row in f_obj_csv:
            yield row["message"]
    else:
        yield from f_obj


def main():
    crons = defaultdict(dict)
    started_our_cron = False
    stopped_our_cron = False
    # Useful to get the cron running during the period that our cron was running too
    our_cron_name = "Sale Subscription: generate recurring invoices and payments"
    with open(sys.argv[1]) as f:
        date_pids_used = []
        for line_no, line in enumerate(lines(f)):
            line = line.strip(' \n"')
            line_separated = line.split("`")
            if "`" not in line:
                continue
            date_pid_match = date_pid_regex.match(line_separated[0])
            if not date_pid_match:
                continue
            date_pid_match = date_pid_match.groups()
            if date_pid_match in date_pids_used:
                continue
            date_pids_used.append(date_pid_match)
            cron_name = line_separated[1]
            key = (cron_name, date_pid_match[1])
            crons[key].setdefault("running", 0)
            if "Starting job " in line_separated[0]:
                if our_cron_name in cron_name:
                    started_our_cron = True
                    stopped_our_cron = False
                if started_our_cron and not stopped_our_cron:
                    print("Starting job", key, "lineno", line_no, " - ", line)
                crons[key]["started"] = line
                crons[key]["running"] += 1
                crons[key]["started_datetime"] = datetime.strptime(date_pid_match[0], datetime_format)
            elif "Job " in line_separated[0]:
                if started_our_cron and not stopped_our_cron:
                    print("Finished job", key, "lineno", line_no, " - ", line)
                if our_cron_name in cron_name:
                    stopped_our_cron = True
                    started_our_cron = False
                crons[key]["finished"] = line
                crons[key]["running"] -= 1
                crons[key]["finished_datetime"] = datetime.strptime(date_pid_match[0], datetime_format)

    top_heavy_crons = []
    for cron_name, step in crons.items():
        if step["running"] == 0 and step.get("finished_datetime") and step.get("started_datetime"):
            diff_s = (step["finished_datetime"] - step["started_datetime"]).seconds
            if diff_s >= 30:
                top_heavy_crons.append([diff_s, cron_name, step])
                # print("cron_name: %s finisehd in %ss" % (cron_name, diff_s))
            continue
        finished = step.get("finished")
        started = step.get("started")
        if finished and started and started <= finished:
            continue
        print(
            "cron_name: %s\nStarted line: %s\nFinished line: %s.\nRunnig: %d\n\n"
            % (cron_name, started, finished or "", step["running"])
        )

    # print(crons)
    if top_heavy_crons:
        top_heavy_crons = sorted(top_heavy_crons)[:30]
        with open("/tmp/borrar.txt", "a") as flog:
            for diff_s, cron_name, step in top_heavy_crons:
                flog.write("%.2fm - %s\n" % (diff_s / 60.0, cron_name))


if __name__ == "__main__":
    main()
