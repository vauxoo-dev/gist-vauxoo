# cbm_ignore

Generate a `.cbmignore` for Odoo containers so `codebase-memory-mcp` indexes the real instance path without loading every cloned repository.

The generated file includes:

- all Odoo core under `/home/odoo/instance/odoo/odoo`;
- only installed Odoo modules from `ir.module.module`;
- unit tests inside real installed modules;
- no Odoo addon modules named `test_*`;
- only `*.py`, `*.xml`, and `*.js` source-like files;
- no `.git`, `__pycache__`, `node_modules`, minified JS, or static vendored libraries.

## Usage

Copy the files into the Odoo instance root inside the container:

```bash
docker cp .cbmignore.jinja absa120:/home/odoo/instance/.cbmignore.jinja
docker cp generate_cbmignore_from_jinja.py absa120:/tmp/generate_cbmignore_from_jinja.py
```

Run as the `odoo` user:

```bash
/home/odoo/instance/odoo/odoo-bin shell --log-level=warn < /tmp/generate_cbmignore_from_jinja.py
```

Then index the real instance path:

```bash
source $MAIN_REPO_FULL_PATH/variables.sh
export PROJECT=${MAIN_APP}_${VERSION}
codebase-memory-mcp cli index_repository --repo_path /home/odoo/instance --name=$PROJECT
```

## Optional Environment Variables

The script defaults to `/home/odoo/instance`, but these variables can override paths:

```bash
export CBM_ODOO_INSTANCE_PATH=/home/odoo/instance
export CBMIGNORE_TEMPLATE=/home/odoo/instance/.cbmignore.jinja
export CBMIGNORE_OUTPUT=/home/odoo/instance/.cbmignore
export CBMIGNORE_BACKUP=/home/odoo/instance/.cbmignore.before-installed-modules
```

## Validation

Confirm the project and scope:

```bash
codebase-memory-mcp cli list_projects | grep -A8 -B2 "$PROJECT"
codebase-memory-mcp cli search_code --project "$PROJECT" --pattern "" --mode=files \
    --path-filter '(^|/)odoo/(odoo/)?addons/test_[^/]+/' --limit 20
codebase-memory-mcp cli search_code --project "$PROJECT" --pattern "class BaseModel" \
    --mode=files --path-filter '^odoo/odoo/models.py$' --limit 5
```

The `test_*` query should return `files: []`; `odoo/odoo/models.py` should be present.
