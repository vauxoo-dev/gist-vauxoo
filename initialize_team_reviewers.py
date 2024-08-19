import os

import gitlab

GITLAB_CFG = os.path.expanduser("~/.python-gitlab.cfg")


# Connect to GitLab instance
gl = gitlab.Gitlab.from_config("default", [GITLAB_CFG])

# Retrieve groups
group_reviewers = gl.groups.get("teams/reviewers")
group_developers = gl.groups.get("teams/developers")
all_groups = gl.groups.list(all=True)

# Grant developer access to the reviewers team in all groups that the developers team already have access
for group in all_groups:
    group = gl.groups.get(group.id)
    if any(g["group_full_path"] == group_developers.full_path for g in group.shared_with_groups):
        print(group.full_path)
        try:
            group.share(group_reviewers.id, group_access=gitlab.const.AccessLevel.DEVELOPER)
        except Exception as err:
            print(err)

# Remove direct access to reviewers to projects, because access is now implicit
reviewer_members = group_reviewers.members.list(all=True)
reviewer_member_ids = {m.id for m in reviewer_members}
# all_projects = gl.projects.list(all=True)
for project in all_projects:
    removed_this_project = []
    for member in project.members.list(all=True):
        if member.id in reviewer_member_ids:
            try:
                member.delete()
            except Exception as err:
                print("Couldn't delete %s from %s: %s" % (member.username, project.name_with_namespace, err))
                continue
            removed_this_project.append(member.username)
    if removed_this_project:
        print("%s: %s" % (project.name_with_namespace, ", ".join(removed_this_project)))
