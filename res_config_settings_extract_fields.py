"""
Server action to output all fields to be included on a ``res.config.settings``
XML data, when initializing a module for an app of an already-existing instance
"""

config = env['res.config.settings']
defaults = config.default_get([])
groups = []
for default, value in defaults.items():
    field = config._fields[default]
    try:
        if value and field.implied_group and not field.default:
            groups.append(default)
    except Exception:  # AttributeError for impliet_group
        continue

# Output XML attributes
output = "\n".join([
    '<field name="%s" eval="True"/>' % group
    for group in groups
])
raise Warning(output)
