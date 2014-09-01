import os
import fileinput
import sys

def replaceAll(file, value):
    for line in fileinput.input(file, inplace=1):
        for keys_prefix in value.keys():
            for dat in value.get(keys_prefix):
                prefijo = keys_prefix
                module = dat
                val = line.split("import")
                if (module in line) and prefijo == "rm":
                    line = ""
                    continue
                if len(val) >= 2 and (module in line.split()) and not(prefijo in line):
                    if prefijo == "openerp.addons":
                        line = line.replace(line, "{} {}.{} import{}".format("from", prefijo, module, val[-1]))
                    if prefijo == "openerp":
                        line = line.replace(line, "{} {}.{} import{}".format("from", prefijo, module, val[-1]))
                    if prefijo == "openerp.report":
                        line = line.replace(line, "{} {} import{}".format("from", prefijo, val[-1]))
        line.replace("pooler.get_pool(cr.dbname).get(", "self.pool.get(")
        sys.stdout.write(line)

modules_dir = sys.argv[1]
for dirpath, dnames, fnames in os.walk(modules_dir):
    for f in fnames:
        if f.endswith(".py"):
            fname = (os.path.join(dirpath, f))
            replaceAll(fname, value = {
                'openerp': ["osv", "tools.translate"],
                "openerp.addons": ["decimal_precision", "report_webkit"],
                "openerp.report":["report_sxw"],
                "rm":["import pooler"],
                #"replace": [('pooler.get_pool(cr.dbname).get(', 'self.pool.get(')]
                })
