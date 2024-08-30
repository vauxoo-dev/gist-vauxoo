import os

import gitlab

GITLAB_CFG = os.path.expanduser("~/.python-gitlab.cfg")

# Connect to GitLab instance
gl = gitlab.Gitlab.from_config("default", [GITLAB_CFG])

# Retrieve TyP's migration issues
project = gl.projects.get("vauxoo/typ")
migration_issues = [
    issue
    for issue in project.issues.list(all=True)
    if issue.iid >= 387
]

# Retrieve milestone "17.0" and assign it to all migration issues
milestone_v17 = next(m for m in project.milestones.list() if m.title == "17.0")
for issue in migration_issues:
    issue.milestone_id = milestone_v17.id
    try:
        _result = issue.save()
    except Exception as err:
        print("Failed:", err)
