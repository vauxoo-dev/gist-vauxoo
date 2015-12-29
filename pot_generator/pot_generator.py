#!/usr/bin/env python
#-*-coding:utf-8-*-

import base64
import os
import subprocess
import oerplib

SERVER = 'localhost'
#DB = raw_input('Write a database name for your webservice, be aware that db will be ERASED:')
DB='ovl70'
PROTOCOL = 'xmlrpc'
PORT = 10000
TIMEOUT = 4000
USER = 'admin'
PASSWD = 'admin'
#SRC_PATH = raw_input('Insert the branch path you are going to scrob for (Remember PATH is absolute):')
SRC_PATH = '/home/hbto/bzr_projects/_VE/70_ovl_branches/ovl70'

oerp = oerplib.OERP(server=SERVER, database=DB, protocol=PROTOCOL, port=PORT, timeout=TIMEOUT)
#<WARNING><ACHTUNG><CUIDADO> DROPING PREVIOUS DB
oerp.db.drop('admin',DB)
##CREATING A NEW DB
oerp.db.create_and_wait('admin',DB, demo_data=False)
user = oerp.login(user=USER, passwd=PASSWD)
#UPDATING MODULE LIST
upd_id = oerp.execute('base.module.update','create',{'state':'init'})
oerp.execute('base.module.update','update_module',upd_id)

#DIRECTORY LIST
src_list = []
if not os.path.exists(SRC_PATH):
    print 'Directory not found: ' + SRC_PATH
dir_names = os.listdir(SRC_PATH)
dir_names = [dir_name for dir_name in dir_names if not dir_name.startswith('.')]
#MODULES INSTALL
module_obj = oerp.get('ir.module.module')
uninstallable_ids = []
installed_dict = {}
installed_dir_names = []
for dir_name in dir_names:
    module_id = module_obj.search([('name', '=', dir_name),('state','!=','uninstallable')])
    if module_id:
        installed_module_id = module_obj.search([('name', '=', dir_name),('state','=','installed')])
        if not installed_module_id:
            try:
                module_obj.button_immediate_install(module_id)
                installed_dir_names.append(dir_name)
                print '[%s] installed successfully'%dir_name.upper()
                installed_dict[dir_name]=module_id[0]
            except:
                uninstallable_ids += module_id
                module_id = module_obj.search([('state','=','to install')])
                print '[%s] unmet dependencies'%dir_name.upper()
                module_obj.button_install_cancel(module_id)
        else:
            print '[%s] already installed'%dir_name.upper()
            installed_dir_names.append(dir_name)
            installed_dict[dir_name]=module_id[0]
    else:
        print '[%s] unavailable to install'%dir_name.upper()

wd = os.getcwd()
go_bzr = False
if os.path.exists(SRC_PATH + '/.bzr'):
    go_bzr = True
    os.chdir(SRC_PATH)

dir_names = installed_dict.keys()
dir_names.sort()
dir_names.reverse()

#POT FILES GENERATION
for dir_name in dir_names:
    directory = '%s/%s'%(SRC_PATH,dir_name)
    if not os.path.exists(directory + '/i18n'):
        new_dir_name = directory + '/i18n'
        os.mkdir(new_dir_name)

    module_ids = oerp.execute('ir.module.module','search',[('name','=',dir_name),('state','=','installed')])
    if not module_ids: continue
    lang_wzd_id = oerp.execute('base.language.export','create',{'lang': '__new__',
                                                                'format' : 'po',
                                                                'modules': [(4,installed_dict[dir_name])]
                                                                })
    oerp.execute('base.language.export','act_getfile',[lang_wzd_id])
    data = oerp.execute('base.language.export','read',lang_wzd_id, ['data'])['data']

    file_name = directory + '/i18n/%s.pot'%dir_name
    file = open(file_name, 'w')
    file.write(base64.decodestring(data))
    file.close()
    print '[%s] pot_file Generated'%dir_name.upper()
    if go_bzr:
        subprocess.call(['bzr', 'add'])
        subprocess.call(['bzr', 'ci', '-m', '[i18n][%s]'%dir_name])

os.chdir(wd)
#BAZAAR
if go_bzr:
    print 'Templating is DONE'
else:
    print '.bzr directory not found. Bazaar actions will not be execute'
