# Install 2to3 and copy this file to ../lib2to3/fixes/fix_imports_odoo.py
# And later run 
#   $2to3 --fix=imports_odoo --no-diffs -w .
"""Fix incompatible imports and module references of odoo."""
from . import fix_imports

MAPPING = {
       # odoo replace
       'osv': 'openerp.osv',
       'tools': 'openerp.tools',
       'decimal_precision': 'openerp.addons.decimal_precision',
       'report_webkit': 'openerp.addons.report_webkit',
       'web': 'openerp.addons.web',
       'report_sxw': 'openerp.report.report_sxw',
       'tools.translate': 'openerp.tools.translate',
    }

class FixImportsOdoo(fix_imports.FixImports):

    run_order = 7.5

    mapping = MAPPING
