#!/usr/local/bin/python3
from __future__ import print_function

import os
from collections import defaultdict

import gitlab


CFG = os.path.expanduser("~/.python-gitlab.cfg")


class GitlabAPI(object):
    def __init__(self):
        self.gl = gitlab.Gitlab.from_config('default', CFG)
        self.access_level_code_name = {
            gitlab.GUEST_ACCESS: 'guest',
            gitlab.REPORTER_ACCESS: 'reporter',
            gitlab.DEVELOPER_ACCESS: 'developer',
            gitlab.MAINTAINER_ACCESS: 'maintainer',
            gitlab.MASTER_ACCESS: 'master',
            gitlab.OWNER_ACCESS: 'owner',
        }
        self.access_level_name_code = {
            v: k for k, v in self.access_level_code_name.items()}

    def get_mr_diff(self, project_name=None):
        project = self.gl.projects.get(project_name)
        # print(gl.projects.list())
        # print(project)
        mrs = project.mergerequests.list(state="opened")
        for mr in mrs:
            # diffs = mr.diffs.list()
            # print(diffs)
            # print(dir(mr))
            for change in mr.changes()['changes']:
                print(change['diff'])
            # for diff in diffs:
                # print(diff)
                # print(dir(diff))
                # print(diff.list())
                # print(diff.short_print())
                # print(diff.display(True))
            # break
        # print(mrs, len(mrs))c

    def get_members_grouped_by_access_level(self, group_id):
        group = self.gl.groups.get(group_id)
        members = group.members.list(all=True, access_level=gitlab.REPORTER_ACCESS)
        get_members_by_access_level = defaultdict(list)
        for member in members:
            access_name = self.access_level_code_name[member.access_level]
            get_members_by_access_level[access_name].append(member)
        return get_members_by_access_level
    
    def delete_reporter_members(self, group_id):
        reporter_members = self.get_members_grouped_by_access_level(group_id).get('reporter', [])
        for member in reporter_members:
            print("Deleting: <%s> %s" % (member.name, member.username))
            member.delete()

if __name__ == '__main__':
    obj = GitlabAPI()
    # obj.delete_reporter_members('vauxoo')
