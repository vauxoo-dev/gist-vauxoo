import re


logfile = "/Users/moylop260/Downloads/job_20_test_all.txt"
re_module_log = r"( openerp.modules.module: module )(?P<module>[\w,\-,\_]+):( creating or updating database tables)"
module_to_search_previous_depends = 'mail_notification_picking'

modules = []
files = []
with open(logfile, "r") as f:
    for line in f.readlines():
        match_object = re.search( re_module_log, line )
        if match_object:
            module = match_object.group("module")
            if not module in modules:
                modules.append( module )
            # files.append( module + '/' + match_object.group("file") )

if module_to_search_previous_depends in modules:
    print ','.join(
        modules[:modules.index(module_to_search_previous_depends) + 1] )

# print '\n'.join(files)
