# Server action to output all modules to be included on the manifest, useful
# when initializing a module for an app of an already-existing instance,
# or when removing superfluous modules

MODNAMES_TO_ADD = []
# Add here app's module name if already installed, so its dependencies are not considered
MODNAMES_TO_IGNORE = [
    # All modules dependn on base anyway
    "base",
    # Don't install it unless necessary, to avoid performance issues
    # If there's no data for it, then it dosen't make sense to have it in CI
    "base_automation",
    # Dependency of OdooStudio, not useful in CI
    "base_import_module",
    # Not useful and deprecated in newer versions anyway
    "odoo_referral",
    "web_dashboard",
    # In case this is run in a test instance on DeployV
    "web_environment_ribbon_isolated",
    # Studio is not useful in CI
    "web_studio",
    "studio_customization",
]


def compute_dependencies(modules):
    """Compute recursive dependencies for the provided modules"""
    dependencies = modules.mapped('dependencies_id.depend_id')
    for x in range(10):  # Didn't want to use while True
        old_dependencies = dependencies
        dependencies |= dependencies.mapped('dependencies_id.depend_id')
        if old_dependencies == dependencies:
            break
    return dependencies


module_obj = env['ir.module.module'].sudo()
installed_modules = module_obj.search([
    ('state', '=', 'installed'),
    ('auto_install', '=', False),
    ('name', 'not in', MODNAMES_TO_IGNORE),
])

# Include only modules that are not already installed by any other module,
# i.e. are not dependencies of any other one
modnames_to_add = []
for module in installed_modules:
    other_modules = installed_modules - module
    other_dependencies = compute_dependencies(other_modules)
    if module not in other_dependencies:
        modnames_to_add.append(module.name)

output = "\n".join([
    '"%s",' % modname
    for modname in sorted(modnames_to_add)
])
raise Warning(output)
