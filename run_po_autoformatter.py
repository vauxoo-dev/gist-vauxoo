from gitlab_api import GitlabAPI

projects_branches = [
    "vauxoo/sbd@14.0",
]
commit_msg = """
[I18n] $module: autoformat translations

This runs the translations autoformatter [1], which performs the
following changes over .po files:
- Sort terms alphabetically
- Split lines to 78 characters
- clear message when translated term is the same as original one

This is done to produce a file as if it were re-exported from Odoo. For
more info, see [2].

[1] https://github.com/OCA/odoo-pre-commit-hooks/pull/76  
[2] https://github.com/Vauxoo/pre-commit-vauxoo/issues/104
"""

gl = GitlabAPI()
gl.make_mr(
    projects_branches=projects_branches,
    commit_msg=commit_msg,
    branch_dev_name="i18n_autoformat-luisg",
    task_id=61194,
    prefix_version=True,
    run_pre_commit_vauxoo=True,
)
