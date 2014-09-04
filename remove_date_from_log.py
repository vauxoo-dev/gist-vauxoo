import re
 
logfile = "/Users/moylop260/Desktop/log1_error.log"
re_module_log = "(openerp)(?P<module>[\D|\d])+"

newfile = open(logfile + '.out', "wb")
with open(logfile, "r") as f:
    for line in f.readlines():
        match_object = re.search( re_module_log, line )
        if match_object:
            newfile.write(match_object.group(0))
    newfile.close()
