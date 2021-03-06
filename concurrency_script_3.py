import logging
import threading
from contextlib import closing

import odoo
from odoo.addons.base.models.ir_sequence import _update_nogap
from psycopg2 import OperationalError

_logger = logging.getLogger(__name__)

THREADS = 5


def update_quant(thread_name, record_id, only_read=False):
    registry = odoo.modules.registry.Registry.new(self.env.cr.dbname)
    with odoo.api.Environment.manage(), closing(registry.cursor()) as new_cr, odoo.tools.mute_logger('odoo.sql_db'):
        # Create a new environment and database cursor
        new_env = odoo.api.Environment(new_cr, self.env.uid, self.env.context)
        quant = new_env['stock.quant'].browse(record_id)
        old_value = quant._get_available_quantity(quant.product_id, quant.location_id, strict=False, allow_negative=True)
        if only_read:
            return old_value
        new_value = old_value
        for i in range(10):  # concurrency attempts
            try:
                with new_cr.savepoint():
                    quant._update_available_quantity(product_id=quant.product_id, location_id=quant.location_id, quantity=1)
                    break
            except OperationalError as pgoe:
                if pgoe.pgcode == '40001':
                    # _logger.info("%s The field was changed after read (repeatable readable issue)", thread_name)
                    return False
        quant.flush()
        new_value = quant._get_available_quantity(quant.product_id, quant.location_id, strict=False, allow_negative=True)
        _logger.info("%s Quant %s  %d -> %d", thread_name, quant, old_value, new_value)
        new_cr.commit()
        return True


def update_seq(thread_name, record_id, only_read=False):
    registry = odoo.modules.registry.Registry.new(self.env.cr.dbname)
    with odoo.api.Environment.manage(), closing(registry.cursor()) as new_cr, odoo.tools.mute_logger('odoo.sql_db'):
        # Create a new environment and database cursor
        new_env = odoo.api.Environment(new_cr, self.env.uid, self.env.context)
        seq = new_env['ir.sequence'].browse(record_id)
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
                    # _logger.info("%s The field was changed after read (repeatable readable issue)", thread_name)
                    return False
        _logger.info("%s Seq %s %d -> %d", thread_name, seq, old_value, seq.number_next)
        new_cr.commit()
        return True

seq_id = self.env['ir.sequence'].search([], limit=1).id
quant = self.env['stock.quant'].search([], limit=1)
quant._merge_quants()
self.env.cr.commit()
quant_id = quant.id

def process():
    thread_name = threading.current_thread().name
    while True:
        if update_seq(thread_name, seq_id):
            break
    while True:
        if update_quant(thread_name, quant_id):
            break


old_seq = update_seq('first value', seq_id, only_read=True)
old_quant = update_quant('first value', quant_id, only_read=True)

threads = []
for i in range(THREADS):
    t = threading.Thread(target=process, name="Thread %d" % (i+1))
    threads.append(t)
    t.start()

[t.join() for t in threads]

new_seq = update_seq('final value', seq_id, only_read=True)
new_quant = update_quant('final value', quant_id, only_read=True)
_logger.info("Sequence. Number of threads %d. Initial value %d Final seq: %d == %d?", THREADS, old_seq, new_seq, old_seq + THREADS)
_logger.info("Quants. Number of threads %d. Initial value %d Final seq: %d == %d?", THREADS, old_quant, new_quant, old_quant + THREADS)
