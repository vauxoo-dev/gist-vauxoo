import os
import sys
from pathlib import Path
from ipykernel.kernelapp import IPKernelApp

sys.path.append('/home/odoo/instance/odoo')

import odoo
from odoo.tools import config

config.parser.prog = f'{Path(sys.argv[0]).name} Shell'
odoo.cli.server.report_configuration()
dbname = os.getenv('ODOO_DB_NAME') or config['db_name']
print(dbname)

local_vars = {
    'openerp': odoo,
    'odoo': odoo,
}

def load_ipython_extension(ip):
    for var_name, var_value in local_vars.items():
        ip.push({var_name: var_value})

if dbname:
    registry = odoo.registry(dbname)
    with registry.cursor() as cr:
        uid = odoo.SUPERUSER_ID
        ctx = odoo.api.Environment(cr, uid, {})['res.users'].context_get()
        env = odoo.api.Environment(cr, uid, ctx)
        local_vars['env'] = env
        local_vars['cr'] = cr
        local_vars['self'] = env.user
        from IPython import get_ipython

        ip = get_ipython()
        if ip is None:
            app = IPKernelApp.instance()
            app.initialize()
            ip = app.shell

        load_ipython_extension(ip)

        app.start()

        cr.rollback()
else:
    exit()

