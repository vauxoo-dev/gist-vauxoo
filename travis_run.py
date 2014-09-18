import os
import yaml
import re
import logging
import stat

_logger = logging.getLogger(__name__)

MAIN_REPO_URL = "https://github.com/odoo-mexico/odoo-mexico.git"
#MAIN_REPO_URL = "https://github.com/OCA/sale-financial.git"
MAIN_BRANCH = "7.0"

#export TRAVIS_HOME=/tmp/home/travis/build
#export TRAVIS_HOME=/tmp/home

if not os.getenv('TRAVIS_HOME'):
    os.environ['HOME'] = os.getcwd()
else:
    os.environ['HOME'] = os.getenv('TRAVIS_HOME')

def log(*l, **kw):
    out = [i if isinstance(i, basestring) else repr(i) for i in l] + \
          ["%s=%r" % (k, v) for k, v in kw.items()]
    _logger.debug(' '.join(out))

def run(l, env=None):
    """Run a command described by l in environment env"""
    log("run", l)
    env = dict(os.environ, **env) if env else None
    if isinstance(l, list):
        print "run lst",' '.join( l )
        #import pdb;pdb.set_trace()
        if env:
            rc = os.spawnvpe(os.P_WAIT, l[0], l, env)
        else:
            rc = os.spawnvp(os.P_WAIT, l[0], l)
    elif isinstance(l, str):
        print "run str", l
        tmp = ['sh', '-c', l]
        if env:
            rc = os.spawnvpe(os.P_WAIT, tmp[0], tmp, env)
        else:
            rc = os.spawnvp(os.P_WAIT, tmp[0], tmp)
    log("run", rc=rc)
    return rc

enviroment_regex_str = "(?P<var>[\w]*)[ ]*[\=][ ]*[\"\']{0,1}(?P<value>[\w\.\-\_/]*)[\"\']{0,1}"
#v1 https://www.debuggex.com/r/IkYbAthaCr2IEGr3
#v2 https://www.debuggex.com/r/PfnMHBP75q0f31pz
#v3 https://www.debuggex.com/r/BoNHngtLPpKbt1eu
#v4 https://www.debuggex.com/r/x1oxs9LDfuW-d8AF
enviroment_regex = re.compile(enviroment_regex_str, re.M)

url_regex = "(?P<host>(git@|https://)([\w\.@]+)(/|:))(?P<owner>[\w,\-,\_]+)/(?P<repo>[\w,\-,\_]+)(.git){0,1}((/){0,1})"
match_object = re.search( url_regex, MAIN_REPO_URL )

os.environ['TRAVIS_BUILD_DIR'] = os.path.join( os.getenv('HOME'), 'travis', 'build', match_object.group("owner"), match_object.group("repo") )
if not os.path.isdir( os.environ['TRAVIS_BUILD_DIR'] ):
    #print "*******************mkdir ", os.environ['TRAVIS_BUILD_DIR']
    os.makedirs( os.environ['TRAVIS_BUILD_DIR'] )
os.chdir( os.environ['TRAVIS_BUILD_DIR'] )

#import pdb;pdb.set_trace()
if not os.path.isdir( os.path.join(os.environ['TRAVIS_BUILD_DIR'], '.git') ):
    run(['git', 'clone', MAIN_REPO_URL, os.environ['TRAVIS_BUILD_DIR']])

run(['git', '--git-dir=%s'%os.path.join(os.environ['TRAVIS_BUILD_DIR'], '.git'), 'checkout', "-f", MAIN_BRANCH])###FIXME: Esta generando los archivos en donde se ejecuta el archivo
run(['git', '--git-dir=%s'%os.path.join(os.environ['TRAVIS_BUILD_DIR'], '.git'), 'pull', 'origin', MAIN_BRANCH])

def run_travis_section(sections, travis_data, hidden_cmds=None):
    if hidden_cmds is None:
        hidden_cmds = []
    fname_sh = '_'.join(sections) + '_cmd.sh'
    with open(fname_sh, "w") as finstall:
        for key, value in env.iteritems():
            finstall.write('export %s="%s"\n'%(key, value ))
        for section in sections:
            scripts = travis_data.get(section, [])
            scripts_filter = []
            for script in scripts:
                if all([ not hidden_cmd in script for hidden_cmd in hidden_cmds]):
                    scripts_filter.append( script )
            finstall.writelines( map( lambda a: str(a) + '\n', scripts_filter ) )
    st = os.stat(fname_sh)
    os.chmod(fname_sh, st.st_mode | stat.S_IEXEC)
    return os.system( os.path.join(os.environ['TRAVIS_BUILD_DIR'], fname_sh) )

hidden_cmds = []
#hidden_cmds = ["travis_install_nightly", "travis_install_mx_nightly", "git clone", "wget "]#second time not download all

fname_travis_yml = os.path.join(os.environ['TRAVIS_BUILD_DIR'], '.travis.yml')
if os.path.isfile( fname_travis_yml ):
    with open(fname_travis_yml, "r") as f_travis_yml:
        travis_data = yaml.load( f_travis_yml )
        for t_env in travis_data.get('env', []):
            #TODO: Make a virtual environment
            try:
                run(["dropdb", "openerp_test"])
            except:
                pass
            env = os.environ
            for var, value in  enviroment_regex.findall( t_env ):
                env[ var ] = value
            run_travis_section(['install', 'script'], travis_data, hidden_cmds=hidden_cmds)
            break#only first time for now. TODO: pyenv
