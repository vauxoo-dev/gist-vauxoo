#! /usr/bin/env python
# -*- encoding: utf-8 -*-

import odoorpc
import click

__version__ = '1.0.0'

# Define a limit of transactions
MAX_LINES = 100000000


def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo('Version: %s' % __version__)
    ctx.exit()


@click.command()
@click.argument('names', nargs=-1)
@click.option("--db", help="DataBase Name")
@click.option("--user", help="Odoo User")
@click.option("--pwd", help="Odoo Password")
@click.option("--port", type=int, help="Port: 8069 by default", default=8069)
@click.option("--host", help="IP: 127.0.0.1 by default", default="127.0.0.1")
@click.option('--version', is_flag=True, callback=print_version,
              expose_value=False, is_eager=True, help='Show version and exit')
def main(names, db=None, user=None, pwd=None, port=None, host=None):

    if db is None:
        print "Database is required"

    if user is None:
        print "Odoo user is required"

    if pwd is None:
        print "Odoo password is required"

    if db is None or user is None or pwd is None:
        quit()

    odoo = odoorpc.ODOO(host, port=port)

    odoo.login(db, user, pwd)

    CrmLead = odoo.env['crm.lead']
    CrmLeadTag = odoo.env['crm.lead.tag']

    count = 0
    for crm_lead_id in CrmLead.search([('partner_id', '!=', False)]):
        lead = CrmLead.browse(crm_lead_id)
        categories = (
            lead.partner_id.commercial_partner_id.category_id.\
            with_context(lang='en_US').mapped('name'))
        crm_lead_tag = CrmLeadTag.search([('name', 'in', categories)])
        if crm_lead_tag:
            lead.write({'tag_ids': [(6, 0, crm_lead_tag)]})
            print '>>>> Added categories %s to lead %s' % (
                categories, lead.name)
            count += 1

        if count == MAX_LINES:
            quit()

    print '>>>> Total leads updated: %d' % (count)


if __name__ == '__main__':
    main()
