# pylint: disable=print-used

"""Get top lines spending time for log of github actions"""

import re
import sys
from datetime import datetime


def parse_dt(line):
    match = re.search(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+Z", line)
    if match:
        timestamp = match.group(0)
        adjusted_timestamp = re.sub(r"(\.\d{6})\d*Z", r"\1Z", timestamp)
        return datetime.strptime(adjusted_timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
    return None


def parse_gh_file(filename):
    log_durations = []

    previous_time = None
    with open(filename) as f_log:
        for no_line, line in enumerate(f_log, start=1):
            current_time = parse_dt(line)
            if current_time and previous_time:
                duration = (current_time - previous_time).total_seconds()
                log_durations.append((no_line - 1, round(duration, 2)))
            previous_time = current_time
    return log_durations


if __name__ == "__main__":
    fname = sys.argv[1]
    for num_line, duration_s in sorted(parse_gh_file(fname), key=lambda x: x[1], reverse=True)[:10]:
        print(f"{fname}:{num_line} duration {duration_s}s")
