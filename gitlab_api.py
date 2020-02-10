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

    def get_mr_diff(self, project_slug='vauxoo/bistro'):
        group, project = project_slug.split('/')
        project = self.gl.projects.get(project)
        # print(gl.projects.list())
        # print(project)
        mrs = project.mergerequests.list(state="opened")
        for mr in mrs:
            diffs = mr.diffs.list()
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


    def get_members_grouped_by_access_level(self, group_name):
        group = self.gl.groups.get(group_name)
        members = group.members.list()
        get_members_by_access_level = defaultdict(list)
        for member in members:
            access_name = self.access_level_code_name[member.access_level]
            get_members_by_access_level[access_name].append(member)
        return get_members_by_access_level


if __name__ == '__main__':
    obj = GitlabAPI()
    members = obj.get_members_grouped_by_access_level('vauxoo')
    for access, groups in members.items():
        print(access, len(groups))
        print(sorted([group.username for group in groups]))
        print("")
    print(len(members))
