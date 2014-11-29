#!/usr/bin/env python
# coding: utf-8

import os

from misc import run, run_output

repos = ["addons-vauxoo", "odoo-mexico", "odoo-venezuela"]
org_prod = "vauxoo"
teams_prod = ["vauxoo-read", "vauxoo-write"]
org_dev = "vauxoo-dev"
teams_dev = ["vauxoo-dev-write"]
branch_list = []
series = ['8.0', '7.0', '6.1', '6.0', '5.0', 'master']
ssh_prod = {'addons-vauxoo':'git@github.com:Vauxoo/addons-vauxoo.git',
            'odoo-mexico':'git@github.com:Vauxoo/odoo-mexico.git',
            'odoo-venezuela':'git@github.com:Vauxoo/odoo-venezuela.git'}
ssh_dev = {'addons-vauxoo':'git@github.com:vauxoo-dev/addons-vauxoo.git',
            'odoo-mexico':'git@github.com:vauxoo-dev/odoo-mexico.git',
            'odoo-venezuela':'git@github.com:vauxoo-dev/odoo-venezuela.git'}

# 1.- Creating repositories
cmd = ["python", "maintainers-tools/tools/create_repo.py", "-l", ','.join(repos), "vauxoo"]
res = run_output(cmd)
print "res", res

# 1.1.- Assigning teams to repositories created
for team_prod in teams_prod:
    cmd = ["python", "maintainers-tools/tools/add_team_repo.py", "-l", ','.join(repos), org_prod, team_prod]
    res = run_output(cmd)
    print "res", res

# 2.- Creating forks
os.environ['PYTHONPATH'] = "/home/vauxoo7/mt_moy"
cmd = ["python", "-c", "from tools import fork_projects;fork_projects.main()", "-l", ','.join(repos), "--org_to", org_dev, "--org_from", org_prod]
res = run_output(cmd)
print "res", res

# 2.1.- Assigning teams to forks
for team_dev in teams_dev:
    cmd = ["python", "maintainers-tools/tools/add_team_repo.py", "-l", ','.join(repos), org_dev, team_dev]
    res = run_output(cmd)
    print "res", res

# 3.- Local bzr2git
cmd = ["python", "gist-vauxoo/bzr2git_script.py", "/home/vauxoo7/migracion"]
run_output(cmd)

# 4.- Push series to vauxoo and MP to vauxoo-dev
def get_base_name(branch_name):
    return branch_name.split('-')[0]

for repo in repos:
    git_tree_path = os.path.join("/home/vauxoo7/migracion", repo, "git_repo_tree")
    git_repo_path = os.path.join("/home/vauxoo7/migracion", repo, "git_repo")

    cmd = ["mkdir", git_tree_path]
    res = run_output(cmd)
    
    cmd = ["git", "init", git_tree_path]
    res = run_output(cmd)
    
    cmd = ["git", "--git-dir=" + os.path.join(git_tree_path, '.git'), "remote", "add", "local", git_repo_path]
    res = run_output(cmd)
    
    cmd = ["git", "--git-dir=" + os.path.join(git_tree_path, '.git'), "remote", "add", repo + 'prod', ssh_prod[repo]]
    res = run_output(cmd)
    
    cmd = ["git", "--git-dir=" + os.path.join(git_tree_path, '.git'), "remote", "add", repo + 'dev', ssh_dev[repo]]
    res = run_output(cmd)
    
    cmd = ["git", "--git-dir=" + os.path.join(git_tree_path, '.git'), "fetch", "--all"]
    res = run_output(cmd)

    cmd = ["git", "--git-dir=" + git_repo_path, "branch"]
    res = run_output(cmd)

    if res:
        branch_list = [str(item).replace('*', '').strip() for item in res.split('\n')][:-1]
        for branch in branch_list:
            cmd = ["git", "checkout", "-f", branch]
            res = run_output(cmd, os.path.join(git_tree_path))
            if branch in series:
                cmd = ["git", "--git-dir=" + os.path.join(git_tree_path, '.git'), "push", "-f", repo + 'prod', branch]
                res = run_output(cmd)
            else:
                cmd = ["git", "--git-dir=" + os.path.join(git_tree_path, '.git'), "push", "-f", repo + 'dev', branch]
                res = run_output(cmd)
                # 5.- generating PR from vauxoo-dev to vauxoo of the MP branches
                os.environ['PYTHONPATH'] = "/home/vauxoo7/maintainers-tools"
                cmd = ["python", "-c", "from tools import create_pull_request;create_pull_request.main()", 
                       get_base_name(branch), org_prod + '/' + repo, org_dev + ':' + branch, branch]
                res = run_output(cmd)
