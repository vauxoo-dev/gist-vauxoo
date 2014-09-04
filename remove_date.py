import re
 
logfile = "/home/julio/Escritorio/runbot.log"
re_module_log = "(openerp)(?P<module>[\D|\d])+"

newfile = open("/home/julio/Documentos/openerp/instancias/7.0/opl-clubj/runbot2.log", "wb")
with open(logfile, "r") as f:
    for line in f.readlines():
        match_object = re.search( re_module_log, line )
        if match_object:
            newfile.write(match_object.group(0))
    newfile.close()
