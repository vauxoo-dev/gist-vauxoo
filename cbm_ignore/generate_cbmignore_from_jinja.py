import os

try:
    from jinja2 import Environment, FileSystemLoader
except ImportError:
    raise RuntimeError("jinja2 is required in the Odoo Python environment")


ROOT = os.environ.get(
    "CBM_ODOO_INSTANCE_PATH",
    os.path.expanduser("~/instance"),
)
SCRIPT_DIR = os.path.dirname(
    os.path.abspath(globals().get("__file__", "/home/odoo/gist-vauxoo/cbm_ignore/generate_cbmignore_from_jinja.py"))
)
TEMPLATE_PATH = os.path.join(SCRIPT_DIR, ".cbmignore.jinja")
OUTPUT_PATH = os.environ.get("CBMIGNORE_OUTPUT", os.path.join(ROOT, ".cbmignore"))
BACKUP_PATH = os.environ.get(
    "CBMIGNORE_BACKUP",
    os.path.join(ROOT, ".cbmignore.before-installed-modules"),
)

SOURCE_GLOBS = ("*.py", "*.xml", "*.js")
CORE_DIRS = ("odoo/odoo",)


def parents(rel):
    parts = rel.split("/")
    current = ""
    result = []
    for part in parts:
        current = part if not current else current + "/" + part
        result.append(current)
    return result


modules = self.env["ir.module.module"].search(
    [("state", "=", "installed")],
    order="name",
)

module_paths = set()
errors = []

for module in modules.mapped("name"):
    if module.startswith("test_"):
        continue

    try:
        module_import = __import__("odoo.addons.%s" % module, fromlist=[""])
        module_path = os.path.dirname(module_import.__file__)
    except Exception as exc:
        errors.append((module, repr(exc)))
        continue

    if module_path.startswith(ROOT + os.sep):
        rel = os.path.relpath(module_path, ROOT).replace(os.sep, "/")
        module_paths.add(rel)

env = Environment(
    loader=FileSystemLoader(os.path.dirname(TEMPLATE_PATH)),
    trim_blocks=True,
    lstrip_blocks=True,
)
env.globals["parents"] = parents

template = env.get_template(os.path.basename(TEMPLATE_PATH))
content = template.render(
    core_dirs=CORE_DIRS,
    module_paths=sorted(module_paths),
    source_globs=SOURCE_GLOBS,
).rstrip() + "\n"

if os.path.exists(OUTPUT_PATH) and not os.path.exists(BACKUP_PATH):
    with open(OUTPUT_PATH, "r") as src, open(BACKUP_PATH, "w") as dst:
        dst.write(src.read())

with open(OUTPUT_PATH, "w") as fh:
    fh.write(content)

print("modules_installed=%d" % len(modules))
print("module_paths=%d" % len(module_paths))
print("file=%s" % OUTPUT_PATH)
print("template=%s" % TEMPLATE_PATH)
print("backup=%s" % BACKUP_PATH)

if errors:
    print("import_errors=%d" % len(errors))
    for module, error in errors[:20]:
        print("import_error %s %s" % (module, error))
