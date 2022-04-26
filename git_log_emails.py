import sys
import re
 

email_re = re.compile(r'Author: (?P<name>.*) <(?P<email>\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b)>', re.M)

# Use "git log |grep "Author" > borrar.txt"

name_emails = set()
with open(sys.argv[1], "r") as f_git_log:
    for line in f_git_log:
        for name_email in email_re.findall(line):
            name_emails.add(name_email)

for name, email in name_emails:
    name_split = name.split(" ")
    if len(name_split) != 2 or '(' in name:
        continue
    print('git log | grep -i "Author.*%s"|grep -v %s' % (name, email))
