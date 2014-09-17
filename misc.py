"""
A few miscellaneous functions (logging, shell command calls, ...).
"""

import fcntl
import logging
import logging.handlers
import re
import signal
import subprocess
import sys
import threading
import time
import os

__all__ = [
    'kill', 'log', 'run', 'run_output', 'get_committer_info', 'underscore', 'dashes', 'has_test_enable_flag', 'has_no_netrpc_flag', 'project_name_from_unique_name',
    'get_revno_info'
    ]

_logger = logging.getLogger('runbot')
_log_formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s: %(message)s')
#_log_handler = logging.StreamHandler(sys.stdout)
if not os.path.exists('run'): 
    os.mkdir('run')
_log_handler = logging.handlers.TimedRotatingFileHandler('run/runbot.log', 'D', 1, 30)
_log_handler.setFormatter(_log_formatter)
_logger.setLevel(logging.INFO)
_logger.addHandler(_log_handler)

log_lock = threading.Lock()
def log(*l,**kw):
    out = []
    t = threading.current_thread()
    if t.name.startswith('runbot-group-worker-'):
        out.append(t.name[13:])
    elif t.name == 'MainThread':
        out.append('main')
    else:
        out.append(t.name)
    for i in l:
        if not isinstance(i,basestring):
            i=repr(i)
        out.append(i)
    out+=["%s=%r"%(k,v) for k,v in kw.items()]
    with log_lock:
        _logger.info(' '.join(out))

def lock(name):
    fd=os.open(name,os.O_CREAT|os.O_RDWR,0600)
    fcntl.lockf(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)

def nowait():
    signal.signal(signal.SIGCHLD, signal.SIG_IGN)

def run(l,env=None):
    log("run",l)
    env = dict(os.environ, **env) if env else None
    if isinstance(l,list):
        if env:
            rc=os.spawnvpe(os.P_WAIT, l[0], l, env)
        else:
            rc=os.spawnvp(os.P_WAIT, l[0], l)
    elif isinstance(l,str):
        tmp=['sh','-c',l]
        if env:
            rc=os.spawnvpe(os.P_WAIT, tmp[0], tmp, env)
        else:
            rc=os.spawnvp(os.P_WAIT, tmp[0], tmp)
    log("run", rc=rc)
    return rc

def kill(pid,sig=signal.SIGKILL):
    try:
        os.kill(pid,sig)
    except OSError:
        pass

def run_output(l, cwd=None):
    log("run_output",l)
    return subprocess.Popen(l, stdout=subprocess.PIPE, cwd=cwd).communicate()[0]

#----------------------------------------------------------
# OpenERP RunBot misc
#----------------------------------------------------------

def underscore(s):
    return s.replace("~","").replace(":","_").replace("/","_").replace(".","_").replace(" ","_")

def dashes(s):
    return s.replace("~","").replace(":","-").replace("/","-").replace(".","-").replace(" ","-").replace("_","-")

def get_committer_info(repo_path):
    committer_name = None
    committer_xgram = None
    committer_email = None

    output = run_output(["bzr", "log", "--long", "-r-1"], cwd=repo_path)

    committer_re = re.compile('committer: *(.+)<(.+)@(.+)>')
    for i in output.split('\n'):
        m = committer_re.match(i)
        if m:
            committer_name = m.group(1).strip()
            committer_xgram = m.group(2)
            committer_email = m.group(2) + '@' + m.group(3)
            break

    return committer_name, committer_xgram, committer_email

def get_revno_info(repo_path):
    revno = False
    output = run_output(["bzr", "revno"], cwd=repo_path)
    revno_re = re.compile('(\d+)')
    for i in output.split('\n'):
        m = revno_re.match(i)
        if m:
            revno = int( m.group(1).strip() )
            break
    return revno

    
def has_test_enable_flag(server_bin_path):
    """
    Test whether an openerp-server executable has the --test-enable flag.
    (When the flag is present, testing for success/failure is done in a
    different way.)
    """
    p1 = subprocess.Popen([server_bin_path, "--help"],
        stdout=subprocess.PIPE)
    p2 = subprocess.Popen(["grep", "test-enable"], stdin=p1.stdout,
        stdout=subprocess.PIPE)
    p1.stdout.close()  # Allow p1 to receive a SIGPIPE if p2 exits.
    output = p2.communicate()[0]
    return output == "    --test-enable       Enable YAML and unit tests.\n"

def has_no_netrpc_flag(server_bin_path):
    """
    Test whether an openerp-server executable has the --no-netrpc flag.
    (When the flag is present, the runbot uses it.)
    """
    p1 = subprocess.Popen([server_bin_path, "--help"],
        stdout=subprocess.PIPE)
    p2 = subprocess.Popen(["grep", "no-netrpc"], stdin=p1.stdout,
        stdout=subprocess.PIPE)
    p1.stdout.close()  # Allow p1 to receive a SIGPIPE if p2 exits.
    output = p2.communicate()[0]
    return output == "    --no-netrpc         disable the NETRPC protocol\n"

def project_name_from_unique_name(unique_name):
    m = re.search("/(openobject|openerp)-(addons|server|client-web|web)/", unique_name)
    if m:
        n = m.group(2)
        if n == 'client-web':
            return 'web'
        else:
            return n
    else:
        return None

