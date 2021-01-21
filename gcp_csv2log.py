"""
Convert Google Cloud Platform log in cvs to postgresql log
"""
import csv
import os

from file_read_backwards import FileReadBackwards


def get_psql_log_from_gcp_csv(gcp_csv_file):

    fname_logs_temp = "postgresql_temp.csv"

    if not os.path.exists(gcp_csv_file):
        return

    with open(gcp_csv_file) as csvfile:
        reader = csv.DictReader(csvfile)
        with open(fname_logs_temp, "a") as log_temp:
            for row in reader:
                log_temp.write("{column} \n".format(column=row["textPayload"]))

    with FileReadBackwards(fname_logs_temp, encoding="utf-8") as frb:
        with open("postgresql.log", "a") as log:
            for line in frb:
                if line and line is not None:
                    log.write("{column} \n".format(column=line))

    if os.path.isfile(fname_logs_temp):
        os.remove(fname_logs_temp)
