"""
Parse a odoo.log file to search when a cron started and finished.
If started but not finished it will be detect as unfinished.

It is checking the following cron _logger.info:
 _logger.info('Starting job `%s`.', job['cron_name'])
   - https://github.com/odoo/odoo/blob/cc47c76ee70ea684ab8352c47d1d06e7d8282b1b/odoo/addons/base/models/ir_cron.py#L226
 _logger.info('Job `%s` done.', job['cron_name'])
"""

from __future__ import print_function
from collections import defaultdict

import re
import sys

date_pid_regex = re.compile(r'^(?:(\d{4}-\d\d-\d\d \d\d:\d\d:\d\d,\d{3}) (\d+) )', re.M)

crons = defaultdict(dict)
with open(sys.argv[1]) as f:
    date_pids_used = []
    for line in f:
        line = line.strip(' \n"')
        line_separated = line.split('`')
        if '`' not in line:
            continue
        date_pid_match = date_pid_regex.match(line_separated[0])
        if not date_pid_match:
            continue
        date_pid_match = date_pid_match.groups()
        if date_pid_match in date_pids_used:
            continue
        date_pids_used.append(date_pid_match)
        key = (line_separated[1], date_pid_match[1])
        crons[key].setdefault('running', 0)
        if 'Starting job ' in line_separated[0]:
            crons[key]['started'] = line
            crons[key]['running'] += 1
        elif 'Job ' in line_separated[0]:
            crons[key]['finished'] = line
            crons[key]['running'] -= 1

for cron_name, step in crons.items():
    if step['running'] == 0:
        continue
    finished = step.get('finished')
    # if finished and step['started'] <= finished:
    #     continue
    print("cron_name: %s\nStarted line: %s\nFinished line: %s.\nRunnig: %d\n\n" % (cron_name, step['started'], finished or '', step['running']))

# print(crons)
