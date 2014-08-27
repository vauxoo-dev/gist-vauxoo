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
                        continue
                if len(val) >= 2 and (module in line.split()) and not(prefijo in line):
                    if prefijo == "openerp.addons":
                        line = line.replace(line, "{} {}.{} import{}".format("from", prefijo, module, val[-1]))
                    if prefijo == "openerp":
                        line = line.replace(line, "{} {}.{} import{}".format("from", prefijo, module, val[-1]))
                    if prefijo == "openerp.report":
                        line = line.replace(line, "{} {} import{}".format("from", prefijo, val[-1]))
        sys.stdout.write(line)

for dirpath, dnames, fnames in os.walk("/home/julio/Documentos/openerp/instancias/7-vauxoo/7.0-addons-vauxoo/"):
    for f in fnames:
        if f.endswith(".py"):
            fname = (os.path.join(dirpath, f))
            replaceAll(fname, value = {
                'openerp': ["osv", "tools.translate"],
                "openerp.addons": ["decimal_precision", "report_webkit"],
                "openerp.report":["report_sxw"],
                "rm":["import pooler"]
                })
