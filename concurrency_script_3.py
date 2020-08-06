import logging
import threading
from contextlib import closing

import odoo
from odoo.addons.base.models.ir_sequence import _update_nogap
from psycopg2 import OperationalError

_logger = logging.getLogger(__name__)

WORKERS = 5


def update_quant(thread_name, only_read=False):
    registry = odoo.modules.registry.Registry.new(self.env.cr.dbname)
    with odoo.api.Environment.manage(), closing(registry.cursor()) as new_cr, odoo.tools.mute_logger('odoo.sql_db'):
        # Create a new environment and database cursor
        new_env = odoo.api.Environment(new_cr, self.env.uid, self.env.context)
        quant = new_env['stock.quant'].search([], limit=1)
        old_value = quant.quantity
        if only_read:
            return old_value
        for i in range(10):  # concurrency attempts
            try:
                with new_cr.savepoint():
                    quant._update_available_quantity(product_id=quant.product_id, location_id=quant.location_id, quantity=1)
                    break
            except OperationalError as pgoe:
                if pgoe.pgcode == '40001':
                    _logger.error("%s The field was changed after read (repeatable readable issue)", thread_name)
                    return False
        quant.flush()
        _logger.warning("%s Quant %s  %d -> %d", thread_name, quant, old_value, quant.quantity)
        new_cr.commit()
        return True


def update_seq(thread_name, only_read=False):
    registry = odoo.modules.registry.Registry.new(self.env.cr.dbname)
    with odoo.api.Environment.manage(), closing(registry.cursor()) as new_cr, odoo.tools.mute_logger('odoo.sql_db'):
        # Create a new environment and database cursor
        new_env = odoo.api.Environment(new_cr, self.env.uid, self.env.context)
        seq = new_env['ir.sequence'].search([], limit=1)
        old_value = seq.number_next
        if only_read:
            return old_value
        for i in range(10):  # concurrency attempts
            try:
                with new_cr.savepoint():
                    _update_nogap(seq, 1)
                    break
            except OperationalError as pgoe:
                if pgoe.pgcode == '40001':
                    _logger.error("%s The field was changed after read (repeatable readable issue)", thread_name)
                    return False
        _logger.warning("%s Seq %s %d -> %d", thread_name, seq, old_value, seq.number_next)
        new_cr.commit()
        return True


def process():
    thread_name = threading.current_thread().name
    while True:
        if update_seq(thread_name):
            break
    while True:
        if update_quant(thread_name):
            break


old_seq = update_seq('first value', only_read=True)
old_quant = update_quant('first value', only_read=True)

threads = []
for i in range(WORKERS):
    t = threading.Thread(target=process, name="Thread %d" % (i+1))
    threads.append(t)
    t.start()

[t.join() for t in threads]

new_seq = update_seq('final value', only_read=True)
new_quant = update_quant('final value', only_read=True)
_logger.warning("Sequence. Workers %d. Initial value %d Final seq: %d == %d?", WORKERS, old_seq, new_seq, old_seq + WORKERS)
_logger.warning("Quants. Workers %d. Initial value %d Final seq: %d == %d?", WORKERS, old_quant, new_quant, old_quant + WORKERS)
