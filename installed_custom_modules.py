# Server action to output all installed modules that are not native, i.e. not maintained by Odoo S.A.
# This is usefuld to be used to fill the whitelist of modules to keep in cleaning migration scripts.

# Known authors used by native modules, in most cases it's Odoo S.A.
NATIVE_MODULE_AUTHORS = {"Odoo S.A.", "odoo S.A", "Odoo SA", "Odoo"}

# Known native modules whose author is not Odoo, e.g. l10n_mx_reports is authored by Vauxoo
NATIVE_MODULES_DIFF_AUTHOR = {
    "l10n_latam_check",
    "l10n_latam_invoice_document",
    "l10n_mx_reports",
    "l10n_pe_edi",
    "l10n_pe_edi_stock",
    "l10n_pe_reports",
}

env.cr.execute(
    """
    SELECT
        name
    FROM
        ir_module_module
    WHERE
        state = 'installed'
        AND latest_version IS NOT NULL
        AND NOT (
            STRING_TO_ARRAY(
                LOWER(regexp_replace(author, ', | / ', ',', 'g')),
                ','
            ) && %(native_module_authors)s
        )
        -- CoA modules are generally not authored by Odoo
        AND name NOT LIKE 'l10n\\___'
        AND name NOT IN %(native_modules_diff_author)s
    ORDER BY
        name;
    """,
    {
        "native_module_authors": [a.lower() for a in NATIVE_MODULE_AUTHORS],
        "native_modules_diff_author": tuple(NATIVE_MODULES_DIFF_AUTHOR),
    },
)
installed_modules = [x[0] for x in env.cr.fetchall()]
result_str = ",\n".join("'%s'" % module for module in installed_modules)
raise UserError(result_str)
