#!/usr/bin/env python
+# coding: utf-8
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

def execute_cmd5(args, working_dir, out_file=None):
    if working_dir:
        os.chdir( working_dir)
    out_file = out_file or '/dev/null'
    if out_file:
        args.extend([">", out_file])
    #args.extend(["2>&1"])
    print "executing: ", ' '.join( args ),
    print " into", working_dir
    os.system( ' '.join( args ) )
    if working_dir:
        os.chdir( current_path )
    out = ''
    if out_file and os.path.isfile( out_file ):
        out = open(out_file).read()
        out = out and out.strip().strip("\n") or ""
    return out

#@argv[1] path with config files
files_cfg_path = sys.argv[1]
print "files_cfg_path",files_cfg_path
for file_cfg in os.listdir(files_cfg_path):
    file_cfg = os.path.join(current_path, files_cfg_path, file_cfg)
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

        def git_init_local_repo(git_repository_path):
            if not os.path.isdir(git_repository_path):
                cmd_args = ["mkdir", "-p", git_repository_path]
                execute_cmd5(cmd_args, working_dir=None)

            if not os.path.isdir(os.path.join(git_repository_path, 'refs')):
                cmd_args = ["git", "--bare", "init", git_repository_path]
                execute_cmd5(cmd_args, working_dir=None)

            #cmd_args = ["git", "config", "--bool", "core.bare", "true"]
            #execute_cmd5(cmd_args, working_dir=git_repository_path)

        def bzr_pull_branch(branch_unique_name, branch_path):
            if not os.path.isdir(branch_path):
                cmd_args = ["mkdir", "-p", branch_path]
                execute_cmd5(cmd_args, working_dir=None)

            if not os.path.isdir( os.path.join(branch_path, '.bzr') ):
                cmd_args = ["bzr", "init", branch_path]
                execute_cmd5(cmd_args, working_dir=None)

            cmd_args = ["bzr", "pull", "--overwrite", "--remember", branch_unique_name]
            execute_cmd5(cmd_args, working_dir=branch_path)

            return True

        try:
            full_global_path_branches = Config.get(section, "full_global_path_branches")
        except ConfigParser.NoOptionError:
            full_global_path_branches = False

        bzr_branches = eval( Config.get(section, "bzr_branches") )
        for (branch_short_name, branch_unique_name) in bzr_branches:
            #branch_test_unique_name = "~vauxoo/addons-vauxoo/6.1"
            branch_unique_name = ':' in branch_unique_name and \
                branch_unique_name[branch_unique_name.index(':') + 1 : ]
            mp_data = LP.get_merge_proposals(branch_unique_name)
            for mp_number in mp_data.keys():
                bzr_branches.append( (branch_short_name + '-MP' + mp_number, 'lp:' + mp_data[mp_number]['name'] ) )
                #print "pull_branch",mp_number, mp_data[mp_number]['name']
                #lp.pull_branch( mp_data[mp_number]['name'],
                    #os.path.join('/tmp',os.path.basename(mp_data[mp_number]['name']))
                    #os.path.join('/tmp', os.path.basename(mp_number))
                #)


        if bzr2git:
            if full_global_path_branches:
                #try:
                #    git_repository = Config.get(section, "git_repository")
                #except ConfigParser.NoOptionError:
                #    git_repository = 'git_repository'
                git_repository = os.path.join( full_global_path_branches, "git_repo" )

                #current_path = full_global_path_branches
                #current_path = os.path.realpath(os.path.join(os.path.dirname(__file__)))
                #current_path = os.path.normpath( os.path.dirname( __file__ ) )

                path_bzr_branches = full_global_path_branches

                if not os.path.isdir(path_bzr_branches):
                    cmd_args = ["mkdir", "-p", path_bzr_branches]
                    execute_cmd5(cmd_args, working_dir=None)

                git_init_local_repo(git_repository)
                for (branch_short_name, branch_unique_name) in bzr_branches:
                    bzr_branch_fullpath = os.path.join( path_bzr_branches, branch_short_name)

                    #bzr_branch_version = bzr_branch.split('-')[0]
                    #git_branch_version = bzr_branch_version
                    if branch_short_name == 'trunk':
                        git_branch_version = 'master'
                    else:
                        git_branch_version = branch_short_name

                    if not os.path.isdir( os.path.join( bzr_branch_fullpath, ".bzr" ) ):
                        cmd_args = ["bzr", "init", bzr_branch_fullpath]
                        execute_cmd5(cmd_args, working_dir=None)

                    if not os.path.isdir( os.path.join( bzr_branch_fullpath, ".git" ) ):
                        cmd_args = ["mkdir", "-p", bzr_branch_fullpath]
                        execute_cmd5(cmd_args, working_dir=None)

                        cmd_args = ["git", "init", bzr_branch_fullpath]
                        execute_cmd5(cmd_args, working_dir=None)

                        old_revno = "0"
                    else:
                        cmd_args = ["bzr", "revno"]
                        old_revno = execute_cmd5(cmd_args, working_dir=bzr_branch_fullpath,\
                            out_file=os.path.join( bzr_branch_fullpath, 'revno_old.txt'))

                    bzr_pull_branch(branch_unique_name, bzr_branch_fullpath)

                    cmd_args = ["bzr", "revno"]
                    new_revno = execute_cmd5(cmd_args, working_dir=bzr_branch_fullpath,\
                        out_file=os.path.join( bzr_branch_fullpath, 'revno_new.txt'))
            
                    if old_revno <> new_revno:
                        cmd_args = ["bzr", "fast-export", "--plain", "-r", \
                            old_revno + '..' +  new_revno, ".", "|", "git", \
                            "fast-import", "--force"]
                        execute_cmd5(cmd_args, working_dir=bzr_branch_fullpath)

                        cmd_args = ["git", "checkout", "-f", "master"]
                        execute_cmd5(cmd_args, working_dir=bzr_branch_fullpath)

                        cmd_args = ["git", "checkout", "-b", str( uuid.uuid4() )]
                        execute_cmd5(cmd_args, working_dir=bzr_branch_fullpath)

                        if git_repository:
                            cmd_args = ["git", "push", "--force", git_repository,\
                                "HEAD:" + git_branch_version]
                            execute_cmd5(cmd_args, working_dir=bzr_branch_fullpath)
        """
        try:
            bzr_path = Config.get(section, "bzr_path")
        except ConfigParser.NoOptionError:
            bzr_path = False

        try:
            Config.options('bzr2git_conf')
            bzr2git_conf = True
        except ConfigParser.NoSectionError:
            bzr2git_conf = False
        if bzr2git_conf:
            try:
                git_path = Config.get(section, "git_path")
            except ConfigParser.NoOptionError:
                git_path = False
            if os.path.exists( git_path ):
                cmd_args = ["git", "fast-export", "-M", "--all", ">", "/tmp/exported.fi"]
        """