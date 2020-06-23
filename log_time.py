#!/usr/bin/env python
from __future__ import print_function
import sys
import re
from datetime import datetime

THRESHOLD = 10
DATETIME_FMT = '%Y-%m-%d %H:%M:%S'
_re_log = r'(?P<date>^\d{4}-\d\d-\d\d \d\d:\d\d:\d\d),\d{3} (?P<session>\d+) (?P<level>WARNING|ERROR|INFO|DEBUG) (?P<db>[0-9a-zA-Z$_\?]+) (?P<module>[0-9a-zA-Z$_\.]+): (?P<message>.*)'
# _re_poll_log = r' (?P<date>\[\d{4}-\d\d-\d\d \d\d:\d\d:\d\d\]|\[\d\d\/[A-Z][a-z][a-z]\/\d{4} \d\d:\d\d:\d\d\]) '


last = None
for line in open(sys.argv[1]):
    line = line.strip()
    date_re = re.match(_re_log, line)
    if not date_re:
        continue
    date_data = date_re.groupdict()
    current = datetime.strptime(date_data['date'], DATETIME_FMT)
    seconds = (current - last).seconds if last != None else 0
    minutes = (seconds % 3600) // 60 if seconds else 0
    if minutes > THRESHOLD:
        print("The following line:\n%s\nSpent %d minutes\n" % (last_line, minutes))
    last = current
    last_line = line
