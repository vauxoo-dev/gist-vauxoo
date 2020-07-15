import logging
import threading
import time
from contextlib import closing
from random import randint

import odoo

_logger = logging.getLogger(__name__)

WORKERS = 5
RECORDS = 2
MAX_SLEEP = 10

def process():
    thread_name = threading.current_thread().name
    registry = odoo.modules.registry.Registry.new(self.env.cr.dbname)
    with odoo.api.Environment.manage(), closing(registry.cursor()) as new_cr:
        # Create a new environment with new cursor database
        new_env = odoo.api.Environment(new_cr, self.env.uid, self.env.context)
        # with_env replace original env for this method
        for record in self.env['res.bank'].with_env(new_env).search([], limit=RECORDS):
            sleep = randint(1, MAX_SLEEP)
            _logger.info("%s - %s - Sleep %ds - Running process...", thread_name, record, sleep)
            record.write({'name': 'Hello world %s!' % thread_name})
            if hasattr(record, 'flush'):  # >=V13.0 to force UPDATE in database
                record.flush()
            time.sleep(sleep)
            _logger.info("%s - %s ...process ran", thread_name, record)
        new_cr.rollback()


threads = []
for i in range(WORKERS):
    t = threading.Thread(target=process, name="Thread %d" % (i+1))
    threads.append(t)
    t.start()

[t.join() for t in threads]
