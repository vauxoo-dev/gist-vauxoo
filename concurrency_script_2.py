import logging
import threading
from contextlib import closing

import odoo

_logger = logging.getLogger(__name__)
WORKERS = 5
RECORDS = 3

def process():
    registry = odoo.modules.registry.Registry.new(self.env.cr.dbname)
    with odoo.api.Environment.manage(), closing(registry.cursor()) as new_cr:
        # Create a new environment with new cursor database
        new_env = odoo.api.Environment(new_cr, self.env.uid, self.env.context)
        # with_env replace original env for this method
        for record in self.env['res.bank'].with_env(new_env).search([], limit=RECORDS):
            data = record.read(['name'])
            _logger.info("Running process... (%s)", data)
            record.write({'name': 'Hello world!'})
            _logger.info("...process ran (%s)", data)


threads = []
for i in range(WORKERS):
    t = threading.Thread(target=process)
    threads.append(t)
    t.start()

[t.join() for t in threads]
