import csv
import re
from dateutil import tz
from datetime import datetime


# TODO: use an advanced regex for database name
odoo_werkzeug_log = re.compile(
    r"^(?:(\d{4}-\d\d-\d\d \d\d:\d\d:\d\d,\d{3}) (\d+) INFO \w+ werkzeug: )(.*)", re.M
)
# werkzeug_log = re.compile(r"\d+.\d+.\d+.\d+ .*GET .* HTTP.* \d\d\d - \d\d \d+.\d+ \d+.\d+")
werkzeug_log = re.compile(
    r'(?P<ip>\d+.\d+.\d+.\d+) - - \[.*\] "GET (?P<url>.*) HTTP.* (?P<response>\d\d\d) - \d\d (?P<time1>\d+.\d+) (?P<time2>\d+.\d+)',
    re.M,
)
min_time_filter = 10  # seconds


def get_werkzeug_log(csvfname):
    with open(csvfname) as csvf:
        csvr = csv.DictReader(csvf)
        for row in csvr:
            line = row["message"]
            odoo_werkzeug_log_match = odoo_werkzeug_log.match(line)
            if not odoo_werkzeug_log_match:
                continue
            werzkeug_line = odoo_werkzeug_log_match.groups()[-1]
            werkzeug_log_match = werkzeug_log.match(werzkeug_line)
            if not werkzeug_log_match:
                continue
            werkzeug_data = werkzeug_log_match.groupdict()

            # removing float separator since that libreoffice issues
            response_time = int(float(werkzeug_data["time2"]))
            if response_time >= min_time_filter:
                log_date_utc_str = odoo_werkzeug_log_match.groups()[0]
                log_date_utc = datetime.strptime(
                    log_date_utc_str, "%Y-%m-%d %H:%M:%S,%f"
                )
                log_date_utc = log_date_utc.replace(tzinfo=tz.tzutc())
                log_date_local = log_date_utc.astimezone(tz.tzlocal())
                print(
                    "%s,%s (local),%s (utc),%s"
                    % (
                        response_time,
                        log_date_local.strftime("%Y-%m-%d %H:%M:%S"),
                        log_date_utc.strftime("%Y-%m-%d %H:%M:%S"),
                        werzkeug_line,
                    )
                )


get_werkzeug_log("/Users/moylop260/Downloads/All-Messages-search-result (28).csv")
