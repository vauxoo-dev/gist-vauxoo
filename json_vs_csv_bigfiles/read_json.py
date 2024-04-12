#!/bin/python3
# pylint:disable=print-used
import json
import os
import resource
import time

import psutil

workdir = os.path.dirname(os.path.realpath(__file__))
os.chdir(workdir)


def memory_usage():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024


start_time = time.time()
with open("data.json") as f:
    data = json.load(f)

for line, row in enumerate(data, 1):
    # Get the second column from the record number 1000
    if line == 1000:
        print(row["column1"])
        break

end_time = time.time()
elapsed_time = end_time - start_time
print("Elapsed time: {:.4f} seconds".format(elapsed_time))

print(f"RAM Memory usage: {int(memory_usage()):,} MB")
print(f"Swap Memory Information: {int(psutil.swap_memory().used/1024):,} MB")
