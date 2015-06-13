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

import argparse
import os
from tempfile import gettempdir

from git_run import GitRun


class GitRmAllLog(object):

    def __init__(self, git_url,
                 root_path=None):
        self.git_url = git_url
        if root_path is None:
            root_path = gettempdir()
        else:
            root_path = os.path.expandvars(
                os.path.expanduser(root_path)
            )
        self.git_run_obj = GitRun(git_url, None)
        self.git_run_obj.path = os.path.join(
            root_path,
            self.git_run_obj.owner,
            self.git_run_obj.repo
        )

    def rm_all_log(self, items):
        self.git_run_obj.update()
        refs = self.git_run_obj.get_ref_data(['refs/heads']).keys()
        for ref in refs:
            self.git_run_obj.checkout_bare(ref)
            self.git_run_obj.run([
                "filter-branch", "-f", "--tree-filter",
                "rm -rf %s" % items, "HEAD"
            ])


def main():
    parser = argparse.ArgumentParser(
        "Remove all git log of a file or folder from"
        " a git repo url")
    parser.add_argument(
        "git_repo_url",
        help="Specify url repository git to work.",
    )
    parser.add_argument(
        "items_to_delete",
        help="Specify files or folders to delete (split with commas).",
    )
    parser.add_argument(
        '--root-path', dest='root_path',
        help="Root path to save scripts generated."
             "\nDefault: 'tmp' dir of your O.S.",
        default=None,
    )
    args = parser.parse_args()
    git_repo_url = args.git_repo_url
    items_to_delete = args.items_to_delete
    root_path = args.root_path
    git_rm_all_log_obj = GitRmAllLog(git_repo_url, root_path)
    git_rm_all_log_obj.rm_all_log(items_to_delete)


if __name__ == '__main__':
    main()
