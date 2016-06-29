import re

logfile = "job_20_test_all.txt"
re_module_log = "(openerp)(?P<module>[\D|\d])+"
re_module_name = re.compile(
    r"(openerp\.modules\.module\: module )(?P<module>(\w|_)+):")

newfile = open(logfile + '.out', "wb")
modules = []
with open(logfile, "r") as flog:
    for line in flog:
        match_object = re.search(re_module_log, line)
        if match_object:
            newfile.write(match_object.group(0))
            match_module = re_module_name.findall(line)
            if match_module:
                modules.append(match_module[0][1])
    newfile.close()

print ','.join(modules)
