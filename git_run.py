#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2013 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: moylop260 (moylop260@vauxoo.com)
############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import os
import re
import subprocess


class GitRun(object):

    def __init__(self, repo_git, path):
        self.repo_git = repo_git
        self.path = path
        self.repo_git_regex = r"(?P<host>(git@|https://)([\w\.@]+)(/|:))" + \
            r"(?P<owner>[~\w,\-,\_]+)/" + \
            r"(?P<repo>[\w,\-,\_]+)(.git){0,1}((/){0,1})"
        match_object = re.search(self.repo_git_regex, repo_git)
        if match_object:
            self.host = match_object.group("host")
            self.owner = match_object.group("owner")
            self.repo = match_object.group("repo")
        else:
            self.host, self.owner, self.repo = False, False, False

    def get_config_data(self, field=None):
        if field is None:
            field = "-l"
        res = self.run(["config", field])
        if res:
            res = res.strip("\n").strip()
        return res

    def run(self, cmd):
        """Execute git command in bash"""
        cmd = ['git', '--git-dir=%s' % self.path] + cmd
        # print "cmd", ' '.join(cmd)
        try:
            return subprocess.check_output(cmd)
        except BaseException:
            return None

    def update(self):
        """Get a repository git or update it"""
        if not os.path.isdir(os.path.join(self.path)):
            os.makedirs(self.path)
        if not os.path.isdir(os.path.join(self.path, 'refs')):
            subprocess.check_output([
                'git', 'clone', '--bare', self.repo_git, self.path
            ])
        self.run(['gc', '--auto', '--prune=all'])
        self.run(['fetch', '-p', 'origin', '+refs/heads/*:refs/heads/*'])
        self.run(['fetch', '-p', 'origin', '+refs/pull/*/head:refs/pull/*'])

    def show_file(self, git_file, sha):
        result = self.run(["show", "%s:%s" % (sha, git_file)])
        return result

    def get_sha(self, revision):
        result = self.run(["rev-parse", revision])
        return result
