from odoo import models


class ResPartner(models.Model):
    _inherit = "res.partner"

    def _xml_data_generator_get_demo_phone(self):
        return "111111111111"

    def _xml_data_generator_get_demo_email(self):
        if self.is_company:
            return "partner_company_email_%s@domain.com" % self.id
        return "partner_email_%s@domain.com" % self.id
