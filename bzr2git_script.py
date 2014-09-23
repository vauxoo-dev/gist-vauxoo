#!/usr/bin/env python
# coding: utf-8
import sys
import os
import subprocess
import uuid
import ConfigParser
import launchpad

Config = ConfigParser.ConfigParser()
#Config.read("addons_vauxoo.conf")
"""Config file example
[bzr2git_conf]
full_global_path_branches = /Users/moylop260/openerp/bzr2git/oml6
bzr_branches = [("trunk", "lp:~openerp-mexico-maintainer/openerp-mexico-localization/trunk"), ("7.0", "lp:~openerp-mexico-maintainer/openerp-mexico-localization/7.0"),]
"""

current_path = os.path.realpath(os.path.join(os.path.dirname(__file__)))
LP = launchpad.LP()
LP.connect()
CHECK_MP = True

#@argv[1] path with config files
files_cfg_path = sys.argv[1]
print "files_cfg_path",files_cfg_path

lock_file = os.path.join(files_cfg_path, "run.lock")
print "check exists lock_file", lock_file
if os.path.isfile(lock_file):
    print "lock_file exists. Running this instance in other side. Skipped script."
    sys.exit(0)
#TODO: Use threading
#TODO: Use git-bzr revno to check diff of revno's

try:
    print "creating lock_file", lock_file
    open( lock_file, "w" )
    for file_cfg in os.listdir(files_cfg_path):
        if os.path.splitext( file_cfg )[1] in ['.cfg', '.conf', '.config']:
            file_cfg = os.path.join(files_cfg_path, file_cfg)
            print "file_cfg",file_cfg
            if os.path.isfile( file_cfg ):
                print "is file"
                Config.read( file_cfg )
                section = "bzr2git_conf"
                try:
                    Config.options(section)
                    bzr2git = True
                except ConfigParser.NoSectionError:
                    bzr2git = False

                try:
                    full_global_path_branches = Config.get(section, "full_global_path_branches")
                except ConfigParser.NoOptionError:
                    full_global_path_branches = False
                #full_global_path_branches = os.path.join("/Users/moylop260/openerp/bzr2git/repo_local", os.path.basename( full_global_path_branches ) )
                bzr_branches = eval( Config.get(section, "bzr_branches") )
                if CHECK_MP:
                    for (branch_short_name, branch_unique_name) in bzr_branches:
                        mp_data = LP.get_merge_proposals(branch_unique_name)
                        for mp_number in sorted( mp_data.keys(), reverse=True ):#Process last MP first. This is faster with new MP.
                            bzr_branches.append( (branch_short_name + '-MP' + mp_number, 'lp:' + mp_data[mp_number]['name'] ) )

                if bzr2git:
                    if full_global_path_branches:
                        git_repository = os.path.join( full_global_path_branches, "git_repo" )

                        path_bzr_branches = full_global_path_branches

                        for (branch_short_name, branch_unique_name) in bzr_branches:
                            branch_short_name = branch_short_name.replace('trunk', 'master')#git fashion
                            bzr_branch_fullpath = os.path.join( path_bzr_branches, branch_short_name, 'bzr')
                            git_branch_fullpath = os.path.join( path_bzr_branches, branch_short_name, 'git')

                            #old_revno = LP.get_branch_revno(bzr_branch_fullpath) or 0
                            LP.pull_branch(branch_unique_name, bzr_branch_fullpath)
                            #bzr_info = launchpad.get_committer_info(bzr_branch_fullpath)
                            #new_revno = LP.get_branch_revno(branch_unique_name)#Too long time to get only revno
                            bzr_new_revno = LP.get_branch_revno(bzr_branch_fullpath) or 0
                            git_commit_count = launchpad.git_get_commit_count(
                                    git_branch_fullpath) or 0
                            bzr_revno_from_git_commit_count = \
                                 launchpad.bzr_get_revno(git_commit_count,
                                     bzr_branch_fullpath) or 0
                            #bzr_revno_from_git_commit_count = "0"#Comment this line
                            print "bzr_revno_from_git_commit_count,bzr_new_revno",\
                                bzr_revno_from_git_commit_count,bzr_new_revno
                            if bzr_revno_from_git_commit_count <> bzr_new_revno:
                                #TODO: Process date, commiter and msg. Because with bzr uncommit;bzr touch borrar;bzr commit -m "borrar";bzr push --overwrite this will fail.
                                # Because is the same quantity of revno count.
                                bzr_revno_from_git_commit_count = 0#Fix error of only detect last change and delete all other ones :(. TODO: Fix get last update changes
                                LP.bzr2git(bzr_branch_fullpath,
                                    git_branch_path=git_branch_fullpath,
                                    revision=str(bzr_revno_from_git_commit_count)\
                                         + '..' +  str(bzr_new_revno),
                                    git_repo_path=git_repository,
                                    git_branch_name=branch_short_name,
                                )
finally:
    os.unlink(lock_file)
