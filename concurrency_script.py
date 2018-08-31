import threading
import openerp
import logging

_logger = logging.getLogger(__name__)
WORKERS = 5
RECORDS = 1

def validate():
    with openerp.api.Environment.manage(), openerp.registry(self.env.cr.dbname).cursor() as new_cr:
        # Create a new environment with new cursor database
        new_env = openerp.api.Environment(new_cr, self.env.uid, self.env.context)
        # with_env replace original env for this method
        for temp_hr_emp in self.env['temp.hr.employee'].with_env(new_env).search([('state', '=', 'to_be_review')], limit=RECORDS):
            _logger.info("Running action_validate of %s", temp_hr_emp)
            temp_hr_emp.action_validate()
        new_cr.rollback()


threads = []
for i in range(WORKERS):
    t = threading.Thread(target=validate)
    threads.append(t)
    t.start()

[t.join() for t in threads]
