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
    """ Custom functions using python-gitlab API

    In order to use the API you need to have a config file in your $HOME, you can find an example here:
    https://python-gitlab.readthedocs.io/en/stable/cli.html#content
    Make sure to have a [default] section as that is the one used in this script. For the 'private_token' you need
    to configure a personal token access from your GitLab account.
    https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html#creating-a-personal-access-token

    e.g. ~/.python-gitlab.cfg
    [default]
    url=https://git.vauxoo.com
    private_token=YOUR_TOKEN # You can create it here: https://git.vauxoo.com/profile/personal_access_tokens
    timeout=5
    """
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
        task_url_tmpl = 'https://www.vauxoo.com/web#id=%s&model=%s&view_type=form'

        project = self.gl.projects.get(project_id)
        mrs = project.mergerequests.list(state='all', scope='all', all=True)

        csv_name = '%s_mrs_%s%s' % (project.name, datetime.now().strftime('%Y-%m-%d_%H-%M-%S'), '.csv')
        with open(csv_name, 'w+', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(
                ['# de MR', 'URL del MR', 'Nombre de persona asignada', 'Título', 'Tarea', 'URL de la tarea', 'Estado',
                 'Etiquetas', 'Fecha de creación', 'Fecha de última actualización', 'Fecha de mezcla'])

            for mr in mrs:
                task_label = task_label_pattern.search(mr.title)
                task_id = ''
                task_url = ''

                if task_label:
                    task_id = task_label[0]
                    task_type = task_label[1]

                    if task_type in ('task', 't'):
                        model = 'project.task'
                    else:
                        model = 'helpdesk.ticket'

                    task_url = task_url_tmpl % (numbers_regex.search(task_id)[0], model)

                merge_date = mr.merged_at[:10] if mr.merged_at else ''

                writer.writerow(
                    [mr.iid, mr.web_url, mr.author['name'], mr.title, task_id, task_url, mr.state,
                     mr.labels, mr.created_at[:10], mr.updated_at[:10], merge_date])

    def get_project_depends(self, fname='oca_dependencies.txt'):
        """Read the content of oca_dependencies.txt file of all
        stable projects and branches"""
        workdir = 'gitlab_content'
        try:
            os.mkdir(workdir)
        except FileExistsError:
            pass
        for project in self.gl.projects.list(all=True):
            if project.path_with_namespace.split('/')[0].strip().endswith('-dev'):
                # Filter "-dev" projects only stable ones
                continue
            # TODO: Get file from branch (currently it is only from project)
            for branch in project.branches.list(all=True):
                # TODO: Use a regex here
                if branch.name not in ['10.0', '11.0', '12.0', '13.0', '14.0']:
                    # Filter only stable branches
                    continue
                try:
                    branch_file = project.files.get(fname, branch)
                except gitlab.exceptions.GitlabGetError:
                    continue
                full_name = "%s_%s_%s" % (project.path_with_namespace, branch.name, branch_file.file_name)
                for invalid_char in '@:/#.':
                    full_name = full_name.replace(invalid_char, '_')
                full_name = os.path.join(workdir, full_name)
                with open(full_name, "wb") as fobj:
                    fobj.write(branch_file.decode())


if __name__ == '__main__':
    obj = GitlabAPI()
    # print([(user['name'], user['email']) for user in obj.get_users('@odoo.com')])
    # obj.project_mrs2csv(516) # MRS from ABSA
    # members_attributes = obj.get_members_attributes('vauxoo')
    # print(members_attributes)
    # members obj.get_members_grouped_by_access_level('vauxoo')
    # obj.delete_reporter_members('vauxoo')
    obj.get_project_depends()
