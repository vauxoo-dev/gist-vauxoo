import os

import gitlab

GITLAB_CFG = os.path.expanduser("~/.python-gitlab.cfg")


# Connect to GitLab instance
gl = gitlab.Gitlab.from_config("default", [GITLAB_CFG])

# Get the source and destination groups by name
src_group_name = "vauxoo-dev"
dst_group_name = "teams/developers"
src_group = gl.groups.get(src_group_name)
dst_group = gl.groups.get(dst_group_name)

# Get the members of the source group
members = src_group.members.list(all=True)
members.sort(key=lambda m: m.username.lower())

# Add each member to the destination group
for member in members:
    try:
        dst_group.members.create(
            {
                "user_id": member.id,
                "access_level": gitlab.const.DEVELOPER_ACCESS,
            }
        )
        print(f"Added member {member.username} to the destination group.")
    except gitlab.exceptions.GitlabCreateError as e:
        print(f"Failed to add member {member.username} to the destination group: {e}")
