import os
import fileinput
import sys

def replaceAll(file, prefijo=""):
    for line in fileinput.input(file, inplace=1):
        if ("import pooler" in line) and prefijo == "rm":
            continue
        if prefijo == "openerp.addons":
            line = line.replace("import decimal_precision as dp", "from openerp.addons.decimal_precision import decimal_precision as dp")
            line = line.replace("from report_webkit import webkit_report", "from openerp.addons.report_webkit import webkit_report")
        if prefijo = "openerp":
            line = line.replace("from osv import osv, fields", "from openerp.osv import osv, fields")
            line = line.replace("from tools.translate import _", "from openerp.tools.translate import _")
        sys.stdout.write(line)

for dirpath, dnames, fnames in os.walk("/home/julio/Documentos/openerp/instancias/7.0/attachent_factura_payroll/l10n-mx-invoice-pdf-formats-7.0_backup/"):
    for f in fnames:
        if f.endswith(".py"):
            fname = (os.path.join(dirpath, f))
            replaceAll(fname, "openerp.addons")
