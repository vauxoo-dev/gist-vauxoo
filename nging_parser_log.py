from collections import defaultdict
import re


lineformat = re.compile(r"(?P<ipaddress>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) - - \[(?P<dateandtime>\d{2}\/[a-z]{3}\/\d{4}:\d{2}:\d{2}:\d{2} (\+|\-)\d{4})\] ((\"(GET|POST) )(?P<url>.+)(http\/2\.0\")) (?P<statuscode>\d{3}) (?P<bytessent>\d+) ", re.IGNORECASE)
data_grouped = defaultdict(int)


with open("request_google.txt", "r") as f_req:
    for line in f_req:
        data = re.match(lineformat, line)
        if not data:
            continue
        # print(data.groupdict())
        data_grouped[(data['url'], data['statuscode'], data['bytessent'])] += 1

        
for key, repeated in sorted(data_grouped.items()):
    if repeated >=4:
        continue
    print(key, repeated)
