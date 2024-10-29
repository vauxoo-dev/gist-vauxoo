# Generate a module list sorted by dependency priority, so modules not inherited by other ones are located before.
# This is useful during migrations, to identify what modules to migrate at first.
#
# The result is output as a CSV and downloaded.

module_base = env.ref("base.module_base")
levels = [module_base]

for x in range(25):
    # Build up next level from current level's downstream dependencies (modules depending on these ones)
    # If some of the downstream dependencies are also present on this level, they're moved to the next one
    current_level = levels.pop()
    new_level = (
        # Passing a known_deps as a workaround, because if a falsy value, current modules are taken instead
        current_level.downstream_dependencies(known_deps=module_base)
        - module_base
    )
    current_level -= new_level
    levels.append(current_level)
    if not new_level:
        break
    levels.append(new_level)

# Exclude native modules from result
known_native_names = [
    "l10n_latam_base",
    "l10n_latam_invoice_document",
    "l10n_mx_reports",
    "l10n_mx_reports_closing",
    "l10n_pe_edi",
    "l10n_pe_reports",
    "sale_subscription",
    # Not actually native from Odoo, but we don't want it to be included
    "web_environment_ribbon_isolated",
]
native_modules = module_base.search(
    [
        ("state", "=", "installed"),
        "|",
        "|",
        "|",
        ("author", "in", ("Odoo S.A.", "Odoo")),
        ("author", "ilike", "Odoo SA"),
        ("name", "in", known_native_names),
        # CoA modules (l10n_XX) are generally not authored by Odoo
        ("name", "=like", "l10n\\___"),
    ]
)
levels_to_output = [level - native_modules for level in levels if level - native_modules]

# Output the result as CSV
out_csv = "Level,Name,Author\n"
for level_number, modules in enumerate(levels_to_output, start=1):
    for module in modules:
        author = ('"%s"' % module.author) if "," in module.author else module.author
        out_csv += "%s,%s,%s\n" % (level_number, module.name, author)

# Create an attachment with the CSV and prompt it to download
attachment_vals = {
    "name": "module_priority_%s.csv" % env.cr.dbname,
    "datas": b64encode(out_csv.encode("utf-8")),
}
attachment = env["ir.attachment"].create(attachment_vals)
action = {
    "type": "ir.actions.act_url",
    "url": "/web/content/%s/%s" % (attachment.id, attachment.name),
    "target": "self",
}
