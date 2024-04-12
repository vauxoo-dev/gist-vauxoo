#!/bin/python3
# pylint:disable=print-used
import csv
import json
import os

workdir = os.path.dirname(os.path.realpath(__file__))
os.chdir(workdir)


def generate_record(num_columns):
    return {f"column{i}": f"Value{i}" for i in range(1, num_columns + 1)}


NUM_COLUMNS = 500
NUM_RECORDS = 100000
# num_columns = 5
# num_records = 10

with open("data.json", "w") as json_file, open("data.csv", "w") as csv_file:
    record_dict = generate_record(NUM_COLUMNS)
    record_json = json.dumps(record_dict)
    for count_record in range(NUM_RECORDS):
        if not count_record:
            # first record
            csv_columns = record_dict.keys()
            writer = csv.DictWriter(csv_file, fieldnames=csv_columns)
            writer.writeheader()
            json_file.write("[\n")
        writer.writerow(record_dict)
        # write directly instead of write all records to save memory
        json_file.write(f"{record_json}")

        if count_record + 1 != NUM_RECORDS:
            # only if it is not the last one
            json_file.write(",\n")
    json_file.write("\n]")

print("JSON & CSV files generated successfully.")
