import threading

from odoo import SUPERUSER_ID, api

# Patch needed in models.py _write_multi meth:
# if self._name == "res.partner" and len(vals_list) == 1 and list(vals_list[0].keys()) == ["write_date"]:
#             return
# Run this code using odoo-bin shell


def create_sales_thread(count):
    with self.pool.cursor() as cr2:  # noqa: F821 pylint: disable=undefined-variable
        new_env = api.Environment(cr2, SUPERUSER_ID, {})
        sale_tmpl = new_env["sale.order"].search([], limit=1, order="id")
        for _i in range(count):
            sale_tmpl.copy()
            cr2.commit()


def main():
    threads = []
    total = 10000
    num_threads = 10
    per_thread = total // num_threads

    for _i in range(num_threads):
        thread = threading.Thread(target=create_sales_thread, args=per_thread)
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()


if __name__ == "__main__":
    main()
