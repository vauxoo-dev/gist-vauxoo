#! /usr/bin/env python
# -*- encoding: utf-8 -*-

import odoorpc
import click


__version__ = '1.0.0'

# Use to create a map with product.template fields and csv headers related
ATTR_2_TMPL_MAPPER = {
    'Normas de referencia': 'alternative_product_ids',
}


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

    ProductTemplate = odoo.env['product.template']
    Attribute = odoo.env['product.attribute']
    AttributeLine = odoo.env['product.attribute.line']

    for attr_name in ATTR_2_TMPL_MAPPER:

        attribute_ids = Attribute.search([('name', '=', attr_name)])
        if not attribute_ids:
            continue

        line_ids = []
        for product_id in ProductTemplate.search([]):
            for line in ProductTemplate.browse(product_id).attribute_line_ids:
                if line.attribute_id.id != attribute_ids[0]:
                    continue
                alternative_product_ids = []
                for name in line.value_ids.mapped('name'):
                    # find product otherwise create then
                    alternative_product = ProductTemplate.search([
                        ('default_code', '=', name)])
                    alternative_product_id = alternative_product and \
                        alternative_product[0] or ProductTemplate.create({
                            'name': name,
                            'default_code': name,
                            'type': 'service',
                            'sale_ok': False,
                            'purchase_ok': False,
                            'categ_id': odoo.env.ref(
                                'inteco.product_category_1_2').id})
                    print '>>>> Alternative product %s: %s' % (
                        alternative_product and 'found' or 'created', name)
                    alternative_product_ids += [(4, alternative_product_id)]
                if alternative_product_ids:
                    ProductTemplate.write(product_id, {
                        'alternative_product_ids': alternative_product_ids})
                line_ids += [line.id]

        # remove attribute lines
        if line_ids:
            AttributeLine.browse(line_ids).unlink()
        # remove attribute
        Attribute.browse(attribute_ids).unlink()


if __name__ == '__main__':
    main()
