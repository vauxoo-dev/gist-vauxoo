#!/usr/bin/env python
from __future__ import print_function
import sys
import re
from datetime import datetime

THRESHOLD = 10
DATETIME_FMT = '%Y-%m-%d %H:%M:%S'
_re_log = r'(?P<date>^\d{4}-\d\d-\d\d \d\d:\d\d:\d\d),\d{3} (?P<session>\d+) (?P<level>WARNING|ERROR|INFO|DEBUG) (?P<db>[0-9a-zA-Z$_\?]+) (?P<module>[0-9a-zA-Z$_\.]+): (?P<message>.*)'
# _re_poll_log = r' (?P<date>\[\d{4}-\d\d-\d\d \d\d:\d\d:\d\d\]|\[\d\d\/[A-Z][a-z][a-z]\/\d{4} \d\d:\d\d:\d\d\]) '

dt2min = lambda current, last: (current - last).seconds / 60.0 if last and current and last != current else 0

first_line = None
first_date = None
last_date = None
last_line = None
for line in open(sys.argv[1]):
    line = line.strip()
    date_re = re.match(_re_log, line)
    if not date_re:
        # print("no matching", line)
        continue
    date_data = date_re.groupdict()
    current = datetime.strptime(date_data['date'], DATETIME_FMT)
    if not first_date:
        first_date = current
        first_line = line
    minutes = dt2min(current, last_date)
    if minutes > THRESHOLD:
        print("The following line:\n%s\nSpent %d minutes\n" % (last_line, minutes))
    last_date = current
    last_line = line
print("\nFirst line:\n", first_line, "\nfirst date\n", first_date)
print("\nLast line:\n", last_line, "\nlast_date\n", last_date)
print("\nTotal time of the file: %d minutes" % (dt2min(last_date, first_date)))
