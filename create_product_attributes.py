#! /usr/bin/env python
# -*- encoding: utf-8 -*-

import odoorpc
import click
import csv

__version__ = '1.0.0'

# Define a limit of products to read from csv file
MAX_LINES = 10000000

# Use to create a map with product.template fields and csv headers related
FIELDS_MAPPER = {
    'name': ['Nombre'],
    'default_code': ['Codigo'],
    'description_sale': ['Objeto y campo de aplicaci\xc3\xb3n'],
    'list_price': ['Precio Final'],
}

# Use to ignore some csv headers
IGNORE_KEYS = ['id', 'Precio']

# Use to ignore attributes with this values
IGNORE_VALS = ['', 'N.A', 'N.A.']

# Attributes type mapper
ATTRIBUTE_TYPE = {
    'select': [
        'Organismo de la norma de correspondencia',
        'Tipo de Norma',
        'Sector',
        'ICS',
    ],
}

# Column in csv that correspond to product category
CATEGORY_KEY = 'Sector'

# CSV file language
LANG = 'es_CR'


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
@click.option("--path", help="Path to CSV file with product data")
@click.option('--version', is_flag=True, callback=print_version,
              expose_value=False, is_eager=True, help='Show version and exit')
def main(names, db=None, user=None, pwd=None, port=None, host=None, path=None):

    if db is None:
        print "Database is required"

    if user is None:
        print "Odoo user is required"

    if pwd is None:
        print "Odoo password is required"

    if path is None:
        print "CSV file is required"

    if db is None or user is None or pwd is None or path is None:
        quit()

    odoo = odoorpc.ODOO(host, port=port)

    odoo.login(db, user, pwd)

    ProductTemplate = odoo.env['product.template']
    ProductProduct = odoo.env['product.product']
    ProductCategory = odoo.env['product.category']
    WebsiteCategory = odoo.env['product.public.category']
    Attribute = odoo.env['product.attribute']
    AttributeValue = odoo.env['product.attribute.value']
    # define a default category
    default_categ_id = odoo.env.ref('inteco.product_category_1_1').id
    website_categ_id = odoo.env.ref('inteco.product_public_category_1').id
    # get all categories that will be used to search in csv data
    categ_ids = WebsiteCategory.search([('parent_id', '=', website_categ_id)])
    categories = {
        categ.with_context(lang=LANG).name.encode('utf8'): categ.id
        for categ in WebsiteCategory.browse(categ_ids)
    }
    all_products = []

    csv_file = open(path, 'r')
    csv_rows = csv.DictReader(csv_file)
    count = 0
    for row in csv_rows:
        # search if category for the row exist on the category list
        categ_id = row[CATEGORY_KEY] in categories and \
            categories[row[CATEGORY_KEY]] or website_categ_id
        # prepare product values
        product_vals = {
            'type': 'service',
            'categ_id': default_categ_id,
            'public_categ_ids': [(6, 0, [categ_id])],
            'website_published': True,
        }
        # avoid use basic fields as attributes
        ignore_attributes = IGNORE_KEYS
        for field, possible_keys in FIELDS_MAPPER.iteritems():
            match = [{field: row[key].replace('\n', '').strip()}
                     for key in row if key in possible_keys]
            product_vals.update(match and match[0] or {})
            ignore_attributes += possible_keys
        attribute_line_ids = []
        for attribute in row:
            if attribute in ignore_attributes:
                continue
            attribute_type = 'hidden'
            for ttype in ATTRIBUTE_TYPE:
                if attribute in ATTRIBUTE_TYPE[ttype]:
                    attribute_type = ttype
            attribute_ids = Attribute.search([('name', '=', attribute)])
            attribute_id = attribute_ids and attribute_ids[0] or \
                Attribute.create({
                    'name': attribute,
                    'type': attribute_type,
                    'create_variant': False})
            value_ids = []
            for attribute_value in row[attribute].split(','):
                if attribute_value.strip() in IGNORE_VALS:
                    continue
                attribute_value_ids = AttributeValue.search([
                    ('name', '=', attribute_value.strip()),
                    ('attribute_id', '=', attribute_id)])
                attribute_value_id = attribute_value_ids and \
                    attribute_value_ids[0] or \
                    AttributeValue.create({
                        'name': attribute_value.strip(),
                        'attribute_id': attribute_id,
                    })
                value_ids += [(4, attribute_value_id)]
            if value_ids:
                attribute_line_ids += [(0, 0, {
                    'attribute_id': attribute_id,
                    'value_ids': value_ids
                })]

        if attribute_line_ids:
            product_vals.update({'attribute_line_ids': attribute_line_ids})

        product_tmpl_ids = ProductTemplate.search([
            ('name', '=', product_vals['name']),
            ('default_code', '=', product_vals['default_code'])])
        if product_tmpl_ids:
            product_tmpl_id = product_tmpl_ids[0]
            ProductTemplate.browse(product_tmpl_id).attribute_line_ids.unlink()
            ProductTemplate.write(product_tmpl_id, product_vals)
            # FIX-ME: apparently when remove attribute is removed the variant
            # now we need to add the default code to the new variant created
            product_variant_id = ProductTemplate.browse(
                product_tmpl_id).product_variant_id.id
            ProductProduct.write(product_variant_id, {
                'default_code': product_vals['default_code']})
            print '>>>> Updated attributes for product:', product_vals['name']
        else:
            product_tmpl_ids = [ProductTemplate.create(product_vals)]
            print '>>>> Created new product:', product_vals['name']

        all_products += product_tmpl_ids

        if count == MAX_LINES:
            quit()

        count += 1

    product_tmpl_ids = ProductTemplate.search([
        ('id', 'not in', all_products),
        ('categ_id', '=', default_categ_id),
    ])

    ProductTemplate.browse(product_tmpl_ids).unlink()
    print '>>>> Products deleted: ', product_tmpl_ids


if __name__ == '__main__':
    main()
