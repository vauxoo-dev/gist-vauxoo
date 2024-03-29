import csv
import os
import re
import sys
from collections import defaultdict
from datetime import datetime

from dateutil import tz

from log_find_cron_unfinished import lines

"""
Open graylog and filter:
 - message:"longpolling" OR message:"werkzeug"
Export CSV file and edit the name of the file
"""

try:
    import geoip2.database
    import geoip2.errors
except ImportError:
    print("Requires 'pip install geoip2==4.5.0'")
    exit(1)


geoip_default_paths = [
    "/usr/share/GeoIP/GeoLite2-City.mmdb",
    "/usr/local/share/GeoIP/GeoLite2-City.mmdb",
]
geoip_path = None
for geoip_default_path in geoip_default_paths:
    if os.path.isfile(geoip_default_path):
        geoip_path = geoip_default_path

if not geoip_path:
    print(
        """Requires download geoip database
GEOIP2_URLS="https://s3.vauxoo.com/GeoLite2-City_20191224.tar.gz https://s3.vauxoo.com/GeoLite2-Country_20191224.tar.gz https://s3.vauxoo.com/GeoLite2-ASN_20191224.tar.gz"
GEOIP_PATH="/usr/local/share/GeoIP"
function geoip_install(){
    URLS="${1}"
    DIR="$( mktemp -d )"
    mkdir -p $GEOIP_PATH
    for URL in ${URLS}; do
        wget -qO- "${URL}" | tar -xz -C "${DIR}/"
        mv "$(find ${DIR} -name "GeoLite2*mmdb")" "$GEOIP_PATH"
    done
    rm -rf "${DIR}"
}
geoip_install "${GEOIP2_URLS}"
    """
    )
    exit(1)

ip_log_re = re.compile(
    r"^(?:(\d{4}-\d\d-\d\d \d\d:\d\d:\d\d,\d{3}) (\d+) INFO .*: (?P<ip>\d+.\d+.\d+.\d+))",
    re.M,
)
only_ip_log_re = re.compile(r"(?P<ip>\d+.\d+.\d+.\d+)")

ip_country = defaultdict(set)


def get_ip_country_log(csvfname):
    geoipdb = geoip2.database.Reader(geoip_path)
    with open(csvfname) as csvf:
        for line in lines(csvf):
            ip_log_match = ip_log_re.match(line) or only_ip_log_re.match(line)
            if not ip_log_match:
                continue
            ip_data = ip_log_match.groupdict()
            ip = ip_data["ip"]
            try:
                country_iso = geoipdb.city(ip).country.iso_code
            except geoip2.errors.AddressNotFoundError:
                # Local IPs
                continue
            ip_country[country_iso] |= {ip}
    for country, ips in ip_country.items():
        print("%s - %s" % (country, ", ".join(ips)))


get_ip_country_log(sys.argv[1])
