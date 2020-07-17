#!/usr/local/bin/python3
from __future__ import print_function

import os
import csv
import re
from datetime import datetime
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
        members = group.members.list(all=True)
        get_members_by_access_level = defaultdict(list)
        for member in members:
            access_name = self.access_level_code_name[member.access_level]
            get_members_by_access_level[access_name].append(member)
        return get_members_by_access_level

    def delete_reporter_members(self, group_id):
        raise UserWarning("""Deleting a group_member will delete project_member too.
                          I mean, if a user was added to custom project_member but
                          it is deleted from group_member so the project_member will be deleted
                          Before to do it you will need get all users added manually to projects of the same group
                          e.g.
                           - vauxoo_group1: member_juan(Reporter)
                           - vauxoo_group1/project1: member_juan(Developer)

                           Running "vauxoo_group1.delete(member_juan)"
                           gitlab api will run "vauxoo_group1/project1.delete(member_juan)" too
                          """)
        reporter_members = self.get_members_grouped_by_access_level(group_id).get('reporter', [])
        for member in reporter_members:
            print("Deleting: <%s> %s" % (member.name, member.username))
            member.delete()

    def get_members_attributes(self, group_id):
        group = self.gl.groups.get(group_id)
        members = group.members.list(all=True)
        return [member.attributes for member in members]

    def get_basic_user_data(self, user):
        return {
            'id': user.id,
            'name': user.name,
            'username': user.username,
            'state': user.state,
            'email': user.email,
        }

    def get_users(self, email_domain=None):
        users = []
        for user in self.gl.users.list(all=True):
            if not email_domain:
                users.append(self.get_basic_user_data(user))
                continue
            if email_domain in user.email:
                users.append(self.get_basic_user_data(user))
        return users

    def project_mrs2csv(self, project_id=None):
        if not project_id:
            return

        task_label_pattern = re.compile(r'(task|t|vx|issue|i|us|hu)[# | -]?\d+', re.IGNORECASE)
        numbers_regex = re.compile(r'\d+')
        task_url_tmpl = 'https://www.vauxoo.com/web#id=%s&model=project.task&view_type=form'

        project = self.gl.projects.get(project_id)
        mrs = project.mergerequests.list(state='all', scope='all', all=True)

        csv_name = '%s_mrs_%s%s' % (project.name, datetime.now().strftime('%Y-%m-%d_%H-%M-%S'), '.csv')
        with open(csv_name, 'w+', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(
                ['# de MR', 'URL del MR', 'Nombre de persona asignada', 'Título', 'Tarea', 'URL de la tarea', 'Estado',
                 'Etiquetas', 'Fecha de creación', 'Fecha de última actualización', 'Fecha de mezcla'])

            for mr in mrs:
                task_id_found = task_label_pattern.search(mr.title)
                task_id = ''
                task_url = ''

                if task_id_found:
                    task_id = task_id_found[0]
                    task_url = task_url_tmpl % numbers_regex.search(task_id)[0]

                merge_date = mr.merged_at[:10] if mr.merged_at else ''

                writer.writerow(
                    [mr.iid, mr.web_url, mr.author['name'], mr.title, task_id, task_url, mr.state,
                     mr.labels, mr.created_at[:10], mr.updated_at[:10], merge_date])



if __name__ == '__main__':
    obj = GitlabAPI()
    print([(user['name'], user['email']) for user in obj.get_users('@odoo.com')])
    # obj.project_mrs2csv(516) # MRS from ABSA
    # members_attributes = obj.get_members_attributes('vauxoo')
    # print(members_attributes)
    # members obj.get_members_grouped_by_access_level('vauxoo')
    # obj.delete_reporter_members('vauxoo')
