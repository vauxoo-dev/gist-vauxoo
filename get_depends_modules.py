import re
 
#logfile = "/Users/moylop260/Desktop/log1.log"
logfile = "/Users/moylop260/Desktop/log1_error.log"
re_module_log = "(: module )(?P<module>[\w,\-,\_]+):( loading )(?P<file>[\w,-,_/.]+)"
module_to_search_previous_depends = 'sale_stock'
 
modules = []
files = []
with open(logfile, "r") as f:
    for line in f.readlines():
        match_object = re.search( re_module_log, line )
        if match_object:
            module = match_object.group("module")
            if not module in modules: 
                modules.append( module )
            files.append( module + '/' + match_object.group("file") )
 
if module_to_search_previous_depends in modules:
    print ','.join( modules[ :modules.index('sale_stock') +1 ] )

print '\n'.join(files)
