import sys
import os
import subprocess
import uuid
import ConfigParser

Config = ConfigParser.ConfigParser()
#Config.read("addons_vauxoo.conf")
"""Config file example
[bzr2git_conf]
#basename_bzr_branch = addons-vauxoo
full_global_path_branches = /Users/moylop260/openerp/bzr2git/addons-vauxoo #All branches from bzr, with name of version
git_repository = git@github.com:Vauxoo/addons-vauxoo.git
"""

def execute_cmd5(args, working_dir, out_file=None):
    if working_dir:
        os.chdir( working_dir)
    out_file = out_file or '/dev/null'
    if out_file:
        args.extend([">", out_file])
    #args.extend(["2>&1"])
    print "executing: ", ' '.join( args )
    os.system( ' '.join( args ) )
    if working_dir:
        os.chdir( current_path )
    out = ''
    if out_file and os.path.isfile( out_file ):
        out = open(out_file).read()
        out = out and out.strip().strip("\n") or ""
    return out

Config.read( sys.argv[1] )
section = "bzr2git_conf"
try:
    Config.options(section)
    bzr2git = True
except ConfigParser.NoSectionError:
    bzr2git = False

def init_local_repo(git_repository_path):
    if not os.path.isdir(git_repository_path):
        cmd_args = ["mkdir", "-p", git_repository_path]
        execute_cmd5(cmd_args, working_dir=None)

    if not os.path.isdir(os.path.join(git_repository_path, 'refs')):
        cmd_args = ["git", "--bare", "init", git_repository_path]
        execute_cmd5(cmd_args, working_dir=None)

    #cmd_args = ["git", "config", "--bool", "core.bare", "true"]
    #execute_cmd5(cmd_args, working_dir=git_repository_path)



try:
    full_global_path_branches = Config.get(section, "full_global_path_branches")
except ConfigParser.NoOptionError:
    full_global_path_branches = False
if bzr2git:
    if full_global_path_branches:
        try:
            git_repository = Config.get(section, "git_repository")
        except ConfigParser.NoOptionError:
            git_repository = 'git_repository'

        current_path = full_global_path_branches
        #current_path = os.path.realpath(os.path.join(os.path.dirname(__file__)))
        #current_path = os.path.normpath( os.path.dirname( __file__ ) )

        path_bzr_branches = current_path

        listdir = os.listdir(path_bzr_branches)
        listdir.reverse()#Master first branch, default branch
        init_local_repo(git_repository)
        for bzr_branch in listdir:
            bzr_branch_fullpath = os.path.join( current_path, bzr_branch)
            bzr_branch_version = bzr_branch.split('-')[0]
            git_branch_version = bzr_branch_version
            if git_branch_version == 'trunk':
                git_branch_version = 'master'
            if os.path.isdir( os.path.join( bzr_branch_fullpath, ".bzr" ) ):

                cmd_args = ["bzr", "revno"]
                old_revno = execute_cmd5(cmd_args, working_dir=bzr_branch_fullpath,\
                    out_file=os.path.join( bzr_branch_fullpath, 'revno_old.txt'))

                if not os.path.isdir( os.path.join( bzr_branch_fullpath, ".git" ) ):
                    cmd_args = ["git", "init", "." ]
                    execute_cmd5(cmd_args, working_dir=bzr_branch_fullpath)

                cmd_args = ["bzr", "pull", ":parent"]
                execute_cmd5(cmd_args, working_dir=bzr_branch_fullpath)

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
                    cmd_args = ["git", "push", "--force", git_repository, "HEAD:"+git_branch_version]
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