# Server action to output all installed modules that are not native, i.e. not maintained by Odoo S.A.
# This is usefuld to be used to fill the whitelist of modules to keep in post SQL migration scripts.

env.cr.execute(
    """
    SELECT
        name
    FROM
        ir_module_module
    WHERE
        state = 'installed'
        AND author NOT IN ('Odoo S.A.', 'Odoo SA', 'Odoo')
        -- CoA modules are generally not authored by Odoo
        AND name NOT LIKE 'l10n\\___'
    ORDER BY
        name;
    """
)
installed_modules = [x[0] for x in env.cr.fetchall()]
result_str = ",\n".join("'%s'" % module for module in installed_modules)
raise UserError(result_str)
