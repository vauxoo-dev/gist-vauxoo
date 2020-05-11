"""
Search and extract all views created by Odoo studio, and output the result
to files grouped by model, e.g.:
- ``account_invoice_views.xml``
- ``res_partner_views.xml``

Replace `YOURMODULE` by the name of the module where views will be placed on.
"""

import os
from lxml import etree, objectify


views = env['ir.ui.view'].search([
    ('name', 'ilike', 'Odoo Studio'),
    ('type', '!=', 'qweb')
])

filenames = []
header = '''<?xml version="1.0" encoding="utf-8"?>
<odoo>
'''
footer = """
</odoo>
"""
for view in views:
    inherited = view.inherit_id
    ext_id = inherited.get_external_id()[inherited.id]
    xml = objectify.fromstring(view.arch)
    indented = (
        etree.tostring(xml, pretty_print=True)
        .decode('utf-8')
        .replace('<data>', '')
        .replace('</data>', '')
        .strip()
        .replace(2*' ', 4*' ')  # Indent with four spaces
        .replace('\n', '\n' + 8*' ')  # Add two indentation levels
    )
    content = '''
    <record id="%s" model="ir.ui.view">
        <field name="name">%s.inherit.YOURMODULE</field>
        <field name="model">%s</field>
        <field name="inherit_id" ref="%s"/>
        <field name="arch" type="xml">
            %s
        </field>
    </record>
''' % (
        ext_id.split('.')[1],
        inherited.name,
        inherited.model,
        ext_id,
        indented,
    )
    filename = '%s_views.xml' % inherited.model.replace('.', '_')
    if not os.path.exists(filename):
        filenames.append(filename)
        content = header + content
    out = open(filename, 'a')
    out.write(content)
    out.close()

# Write footers
for filename in filenames:
    out = open(filename, 'a')
    out.write(footer)
    out.close()
