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
                if ("LocalService" in line) and ('workflow' in line):
                    line = line.replace(line, "{}= {}\n".format( line.split('=')[0], "workflow" ))
                    
                if (module in line) and prefijo == "rm":
                    data = line.split(',')
                    if any([('pooler' in dat_pooler) for dat_pooler in data]):
                        if len(data) > 1:
                            data_str = data[0].replace('pooler', '')
                            line = line.replace(line, "{}{}".format(data_str, data[-1].replace(" ", "")))
                        else:
                            line = ""
                            continue
                    if ('import' in line) and ('netsvc' in line):
                        line = line.replace(module, 'workflow')
                if len(val) >= 2 and (module in line.split()) and not(prefijo in line):
                    if prefijo == "openerp.addons":
                        line = line.replace(line, "{} {}.{} import{}".format("from", prefijo, module, val[-1]))
                    if prefijo == "openerp":
                        line = line.replace(line, "{} {}.{} import{}".format("from", prefijo, module, val[-1]))
                    if prefijo == "openerp.report":
                        line = line.replace(line, "{} {} import{}".format("from", prefijo, val[-1]))
                if 'pooler.get_pool(cr.dbname)' in line:       
                    line.replace('pooler.get_pool(cr.dbname)', 'self.pool.get(')
                if "import pyPdf" in line:
                    line = line.replace(line, 'import pyPdf\n')
        line.replace("from l10n_mx_invoice_amount_to_text import amount_to_text_es_MX", "from openerp.addons.l10n_mx_invoice_amount_to_text import amount_to_text_es_MX")#TODO: check import of modules
        sys.stdout.write(line)

modules_dir = sys.argv[1]
for dirpath, dnames, fnames in os.walk(modules_dir):
    for f in fnames:
        if f.endswith(".py"):
            fname = (os.path.join(dirpath, f))
            replaceAll(fname, value = {
                'openerp': ["osv", "tools.translate"],
                "openerp.addons": ["decimal_precision", "report_webkit", "web"],
                "openerp.report": ["report_sxw"],
                "rm": ["import pooler", "netsvc"],
                #"replace": [('pooler.get_pool(cr.dbname).get(', 'self.pool.get(')]
                })
