from launchpadlib.launchpad import Launchpad, EDGE_SERVICE_ROOT
import os
import threading
import time
import sys

from misc import *

NEW_MERGE_STATUS = ['Needs review', 'Code failed to merge', 'Approved']
MAX_MP = 10

def assert_main_thread():
    t = threading.current_thread()
    #assert t.name == 'MainThread'

def run(l, env=None):
    """Run a command described by l in environment env"""
    log("run", l)
    env = dict(os.environ, **env) if env else None
    if isinstance(l, list):
        if env:
            rc = os.spawnvpe(os.P_WAIT, l[0], l, env)
        else:
            rc = os.spawnvp(os.P_WAIT, l[0], l)
    elif isinstance(l, str):
        tmp = ['sh', '-c', l]
        if env:
            rc = os.spawnvpe(os.P_WAIT, tmp[0], tmp, env)
        else:
            rc = os.spawnvp(os.P_WAIT, tmp[0], tmp)
    log("run", rc=rc)
    return rc

def mkdirs(dirs):
    for d in dirs:
        if not os.path.exists(d):
            os.makedirs(d)

class LP(object):
    """
    Expose the few bits we need from launchpadlib.

    Note: any access to launchpad is done in the same thread.
    """

    def __init__(self):
        assert_main_thread()
        self.con = None
        # Mapping team name - last query time to Launchpad
        self.last_lp_call_per_team = {}

    def connect(self):
        assert_main_thread()
        #launchpad = Launchpad.login_anonymously(
        #    'openerp-runbot', 'edge', 'lpcache')
        cachedir = os.path.expanduser("~/.launchpadlib/cache")
        lp_creds = os.path.expanduser("~/.launchpadlib/.lp_creds")
        self.con = Launchpad.login_with(
            'openerp-runbot', EDGE_SERVICE_ROOT, cachedir,
            credentials_file=lp_creds)

    def get_team_branches(self, team_name):
        assert_main_thread()
        try:
            team = self.con.people[team_name]
        except Exception, e: # What's the proper raised exception?
            log("WARNING: no such team:", team_name)
            return []

        default_branch_filter = {'status': ['Experimental', 'Development', 'Mature']}
        last_lp_call = self.last_lp_call_per_team.get(team_name)
        if not last_lp_call:
            team_branches = team.getBranches(**default_branch_filter)
        else:
            team_branches = team.getBranches(
                modified_since=last_lp_call,
                **default_branch_filter)
        self.last_lp_call_per_team[team_name] = time.strftime('%Y-%m-%d')
        return team_branches

    def get_branch(self, unique_name):
        assert_main_thread()
        return self.con.branches.getByUniqueName(unique_name=unique_name)

    def pull_branch(self, unique_name, repo_path):
        #log("branch-update",branch=unique_name)
        #repo_path = b.repo_path + job_suffix
        if os.path.exists(repo_path):
            log("bzr pull " + repr(["bzr", "pull", "lp:%s" % unique_name, "--quiet", "--remember", "--overwrite", "-d", repo_path]) )
            rc = run(["bzr", "pull", "lp:%s" % unique_name, "--quiet", "--remember", "--overwrite", "-d", repo_path])
        else:
            mkdirs(repo_path)
            log("bzr branch " + repr( ["bzr", "branch", "--quiet", "--no-tree", "lp:%s" % unique_name, repo_path ] ) )
            
            rc = run(["bzr", "branch", "--quiet", "--no-tree", "lp:%s" % unique_name, repo_path ])
        """
        committer_name, committer_xgram, committer_email = \
            get_committer_info(repo_path)
        b.committer_name = committer_name
        b.committer_xgram = committer_xgram
        b.committer_email = committer_email
        log("get-commiter-info", name=committer_name, xgram=committer_xgram, email=committer_email)
        
        log("get-revno-info "+ unique_name)
        revno = get_revno_info( repo_path )
        if revno and b.local_revision_count != revno:
            log("set-revno-info "+ unique_name + " - current revno:" + repr(b.local_revision_count) + " - new revno: " + repr( revno ) )
            b.local_revision_count = revno
        else:
            log("set-revno-info "+ unique_name + " no changes of revno.")
        """
        return True

    def get_merge_proposals(self, unique_name, filters=None, max_mp=None):
        if filters is None:
            filters = {'status': NEW_MERGE_STATUS}
        if max_mp is None:
            max_mp = MAX_MP
        branch = self.get_branch(unique_name)
        merge_proposals = branch.getMergeProposals(**filters)
        mp_number__mp_obj_dict = dict([(merge_proposal.web_link.split('/')[-1], merge_proposal) for merge_proposal in merge_proposals])
        mp_numbers_sort = sorted( mp_number__mp_obj_dict.keys(), reverse=True )
        mp_data = {}
        for mp_number in mp_numbers_sort[:max_mp]:#last MP
            merge_proposal = mp_number__mp_obj_dict[ mp_number ]
            mp_data[mp_number] = {
                'name': merge_proposal.source_branch.unique_name,
                'mp_obj': merge_proposal,
            }
            #merge_proposal = mp_number__mp_obj_dict[ mp_number ]
            #new_branch = merge_proposal.source_branch.unique_name
        #    print "new_branch",mp_number, new_branch
        #lp.pull_branch(branch.complete_name, branch_path)
        return mp_data

    def bzr2git(self, bzr_branch_path, git_repo_path, branch_short_name=None):
        pass#TODO

if __name__ == '__main__':
    lp = LP()
    lp.connect()#TODO: Add to a global variable
    branch_test_unique_name = "~vauxoo/addons-vauxoo/6.1"
    mp_data = lp.get_merge_proposals(branch_test_unique_name)
    for mp_number in mp_data.keys():
        print "pull_branch",mp_number, mp_data[mp_number]['name']
        lp.pull_branch( mp_data[mp_number]['name'],
            #os.path.join('/tmp',os.path.basename(mp_data[mp_number]['name']))
            os.path.join('/tmp',os.path.basename(mp_number))
        )
