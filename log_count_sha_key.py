"""Count the number of occurrences of the "key" of the graylog csv file
to know where a query is executed too many times

A similar patch is needed in production:
 - https://github.com/Vauxoo/odoo/pull/547
"""

import csv
import re
import sys
from collections import OrderedDict, defaultdict

limit_lines = 10000000
fname = sys.argv[1]
with open(fname) as csvfile:
    reader = csv.DictReader(csvfile)

    counter = defaultdict(int)
    sha_message = {}
    line_no = 0
    for row in reader:
        message = row["message"]
        match = re.search(r"key: (\w+)", message)

        if not match:
            continue

        line_no += 1

        if line_no >= limit_lines:
            break

        key = match.groups()[0]
        counter[key] += 1
        if key not in sha_message:
            sha_message[key] = message


counter_ordered = OrderedDict(sorted(counter.items(), key=lambda item: item[1], reverse=True))
limit = 10
for line_no, (key, key_count) in enumerate(counter_ordered.items()):
    if line_no > limit:
        break
    print(f"count {key_count}, sha {key}\n{sha_message[key]}\n\n")
