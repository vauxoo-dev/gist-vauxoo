"""
Server action to output all modules to be included on the manifest, useful
when initializing a module for an app of an already-existing instance
"""

MODNAMES_TO_ADD = ['company_country']
MODNAMES_TO_IGNORE = ['base', 'web_studio', 'studio_customization']


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
modules_to_add = module_obj
for module in installed_modules:
    other_modules = installed_modules - module
    other_dependencies = compute_dependencies(other_modules)
    if module not in other_dependencies:
        modules_to_add |= module

# sorted is not available here, so using a little hack, creating dummy records
# Not using search and sorted because all modules might not be available
not_available = set(MODNAMES_TO_ADD) - set(installed_modules.mapped('name'))
modules_to_add |= module_obj.concat(*[
    module_obj.new({'name': modname})
    for modname in not_available
])

output = "\n".join([
    "'%s'," % module.name
    for module in modules_to_add.sorted('name')
])
raise Warning(output)
