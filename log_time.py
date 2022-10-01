#!/usr/bin/env python
from __future__ import print_function

import re
import sys
from collections import defaultdict
from datetime import datetime

THRESHOLD = 3
DATETIME_FMT = "%Y-%m-%d %H:%M:%S"
_re_log = r"(?P<date>^\d{4}-\d\d-\d\d \d\d:\d\d:\d\d),\d{3} (?P<session>\d+) (?P<level>WARNING|ERROR|INFO|DEBUG) (?P<db>[0-9a-zA-Z$_\?]+) (?P<module>[0-9a-zA-Z$_\.]+): (?P<message>.*)"
# _re_poll_log = r' (?P<date>\[\d{4}-\d\d-\d\d \d\d:\d\d:\d\d\]|\[\d\d\/[A-Z][a-z][a-z]\/\d{4} \d\d:\d\d:\d\d\]) '
_re_test = r"((?P<class>(\w|\.)+)\: Ran \d+ (test|tests) in (?P<time>(\d+.\d+))s)"
_re_test_140 = r"(\: Module (?P<class>(\w+)) loaded in \d+.\d+s \(incl\. (?P<time>(\d+.\d+))s test\))"

dt2min = lambda current, last: (current - last).seconds / 60.0 if last and current and last != current else 0


def remove_color(line):
    WHITE = "\x1b[1;49m"
    GREEN = "\x1b[1;32m"
    # YELLOW =
    # RED =
    CLEAR = "\x1b[0m"
    colors = [WHITE, CLEAR, GREEN]
    for color in colors:
        line = line.replace(color, "")
    return line


first_line = None
first_date = None
last_date = None
last_line = None
module_time = defaultdict(int)
test_time = defaultdict(float)
for line in open(sys.argv[1]):
    line = line.strip()
    # remove colors in the log
    line = remove_color(line)
    date_re = re.match(_re_log, line)
    if not date_re:
        # print("no matching", line)
        continue
    date_data = date_re.groupdict()
    current = datetime.strptime(date_data["date"], DATETIME_FMT)
    if not first_date:
        first_date = current
        first_line = line
    minutes = dt2min(current, last_date)
    module_time[date_data["module"]] += round(minutes, 2)
    if minutes > THRESHOLD:
        print("The following line:\n%s\nSpent %d minutes\n" % (last_line, minutes))

    test_line = re.search(_re_test, line) or re.search(_re_test_140, line)
    if test_line:
        test_line_data = test_line.groupdict()
        test_time[test_line_data["class"]] += float(test_line_data["time"]) / 60.0
    last_date = current
    last_line = line
print("\nFirst line:\n", first_line, "\nfirst date\n", first_date)
print("\nLast line:\n", last_line, "\nlast_date\n", last_date)
print("\nTotal time of the file: %d minutes" % (dt2min(last_date, first_date)))

print(
    "\nModule time %s"
    % {
        key: round(value, 2)
        for key, value in sorted(module_time.items(), key=lambda item: item[1], reverse=True)
        if value >= THRESHOLD
    }
)
print(
    "\nTest time %s"
    % {
        key: round(value, 2)
        for key, value in sorted(test_time.items(), key=lambda item: item[1], reverse=True)
        if value >= THRESHOLD
    }
)
