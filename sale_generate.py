# Run this code using odoo-bin shell
import logging
import threading
from unittest.mock import patch

from odoo import SUPERUSER_ID, api, models

_logger = logging.getLogger(__name__)

_original_write_multi = models.Model._write_multi


def _patched_write_multi(self, vals_list):
    """Odoo is writing write_date in the partner when a sale order is created
    It does not allow to create multiple sale order at the same time
    This patch bypassing the write when only is storing write_date in the partner
    in order to be compatible with multiple threads
    """
    if self._name == "res.partner" and len(vals_list) == 1 and list(vals_list[0].keys()) == ["write_date"]:
        return
    return _original_write_multi(self, vals_list)


def create_sales_thread(count):
    with self.pool.cursor() as cr2:  # noqa: F821 pylint: disable=undefined-variable
        new_env = api.Environment(cr2, SUPERUSER_ID, {})
        sale_tmpl = new_env["sale.order"].search([], limit=1, order="id")
        for _i in range(count):
            new_so = sale_tmpl.copy()
            _logger.info("Sale Order ID: %s created", new_so.id)
            cr2.commit()


def main():
    threads = []
    total = 200000
    num_threads = 20
    per_thread = total // num_threads
    with patch("odoo.models.Model._write_multi", new=_patched_write_multi):
        for _i in range(num_threads):
            thread = threading.Thread(target=create_sales_thread, args=(per_thread,))
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()


if __name__ == "__main__":
    main()
