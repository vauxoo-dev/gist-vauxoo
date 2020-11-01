# Server action to output all modules to be included on the manifest, useful
# when initializing a module for an app of an already-existing instance

MODNAMES_TO_ADD = []
MODNAMES_TO_IGNORE = ['base', 'base_automation', 'web_dashboard', 'web_studio', 'studio_customization']


def compute_dependencies(modules):
    """Compute recursive dependencies for the provided modules"""
    dependencies = modules.mapped('dependencies_id.depend_id')
    for x in range(10):  # Didn't want to use while True
        old_dependencies = dependencies
        dependencies |= dependencies.mapped('dependencies_id.depend_id')
        if old_dependencies == dependencies:
            break
    return dependencies


module_obj = env['ir.module.module']
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
    "'%s'," % modname
    for modname in sorted(modnames_to_add)
])
raise Warning(output)
