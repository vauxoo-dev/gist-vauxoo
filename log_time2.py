# pylint:disable=print-used
from __future__ import print_function

from collections import defaultdict

import re
import sys

# minutes
THRESHOLD = 0.001
# Maximum results
TOP = 1000

RE_MODULE_140 = r"Module (?P<module>(\w+)) loaded in (?P<time>(\d+.\d+))s"
RE_TEST_140 = r"(\: Module (?P<class>(\w+)) loaded in \d+.\d+s \(incl\. (?P<time>(\d+.\d+))s test\))"

WHITE = "\x1b[1;49m"
GREEN = "\x1b[1;32m"
# YELLOW =
# RED =
CLEAR = "\x1b[0m"


def remove_color(line):
    colors = [WHITE, CLEAR, GREEN]
    for color in colors:
        line = line.replace(color, "")
    return line


def log_stats():
    module_time = defaultdict(float)
    test_time = defaultdict(float)
    with open(sys.argv[1]) as flog:
        for line in flog:
            line = line.strip()
            line = remove_color(line)
            module_line = re.search(RE_MODULE_140, line)
            if module_line:
                module_data = module_line.groupdict()
                module_time[module_data["module"]] += float(module_data["time"]) / 60.0
            test_line = re.search(RE_TEST_140, line)
            if test_line:
                test_data = test_line.groupdict()
                test_time[test_data["class"]] += float(test_data["time"]) / 60.0
    module_stats = [
        (key, round(value, 2))
        for key, value in sorted(module_time.items(), key=lambda item: item[1], reverse=True)
        if round(value, 2) >= THRESHOLD
    ][:TOP]
    test_stats = [
        (key, round(value, 2))
        for key, value in sorted(test_time.items(), key=lambda item: item[1], reverse=True)
        if round(value, 2) >= THRESHOLD
    ][:TOP]
    print("\n- module_stats\nsum %f", module_stats, sum(value for key, value in module_stats))
    print("\n- test_stats\nsum %f", test_stats, sum(value for key, value in test_stats))


def main():
    log_stats()


if __name__ == "__main__":
    main()
