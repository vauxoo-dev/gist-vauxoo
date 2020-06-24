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


crons = defaultdict(dict)
with open("/home/odoo/odoo.log") as f:
    for line in f:
        if '`' not in line:
            continue
        line = line.strip(' \n')
        line_separated = line.split('`')
        crons[line_separated[1]].setdefault('running', 0)
        if 'Starting job ' in line_separated[0]:
            crons[line_separated[1]]['started'] = line
            crons[line_separated[1]]['running'] += 1
        elif 'Job ' in line_separated[0]:
            crons[line_separated[1]]['finished'] = line
            crons[line_separated[1]]['running'] -= 1

for cron_name, step in crons.items():
    if step['running'] == 0:
        continue
    finished = step.get('finished')
    # if finished and step['started'] <= finished:
    #     continue
    print("cron_name: %s\nStarted line: %s\nFinished line: %s.\nRunnig: %d\n\n" % (cron_name, step['started'], finished or '', step['running']))
