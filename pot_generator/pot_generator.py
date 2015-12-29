#!/usr/bin/python
# -*- coding: utf-8 -*-
# PYTHON_ARGCOMPLETE_OK
import argparse
import argcomplete
import os
import base64
import subprocess
import oerplib


class PotGenerator(object):

    """
    This object pretend to generate the pot files for a given module.
    """

    epilog = (
        "Odoo Developer Comunity Tool\n"
        "Contributors:\n"
        " - Saul Gonzalez\n"
        " - Katherine Zaoral <kathy@vauxoo.com> (github@zaoral)\n"
        "Source code at git@github.com:vauxoo-dev/gist-vauxoo\n")

    def __init__(self):
        """
        Initialization of the class.
        @return: None
        """
        self.args = self.argument_parser()
        if self.args.get('no_confirm', False):
            pass
        else:
            self.confirm_run(self.args)
        return None

    def argument_parser(self):
        """
        This function create the help command line, manage and filter the
        parameters of this script (default values, choices values).
        @return dictionary of the arguments.
        """
        parser = argparse.ArgumentParser(
            prog='pot-generator',
            description='Generate por file for a given module or module path',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog=self.epilog)

        parser.add_argument(
            '--no-confirm',
            action='store_true',
            help='Ask user for confirmation to the user. Default is True')

        parser.add_argument(
            '-s', '--server',
            metavar='SERVER',
            type=str,
            default='localhost',
            help='The server name where the odoo instance is running')

        parser.add_argument(
            '-d', '--db',
            metavar='DATABASE',
            type=str,
            default='openerp_test',
            help='The database where will be extract the pot files')

        parser.add_argument(
            '-p', '--port',
            metavar='PORT',
            type=str,
            default='8069',  # TODO verify is this is or is another port? 10000
            help='Port to use to connect to the database')

        parser.add_argument(
            'module-path',
            metavar='MODULE PATH',
            type=str,
            help='The module path')

        argcomplete.autocomplete(parser)
        return parser.parse_args().__dict__

    def confirm_run(self, args):
        """
        Manual confirmation before runing the script. Very usefull.
        @param args: dictionary of arguments.
        @return True or exit the program in the confirm is no.
        """
        print'\n... Configuration of Parameters Set'
        for (parameter, value) in args.iteritems():
            print '%s = %s' % (parameter, value)

        question = 'Confirm the run with the above parameters?'
        answer = 'The script parameters were confirmed by the user'
        self.confirmation(question, answer)
        return True

    def confirmation(self, question, answer):
        """
        Manual confirmation for the user.
        @return True or exit the program in the confirmation in negative.
        """
        confirm_flag = False
        while confirm_flag not in ['y', 'n']:
            confirm_flag = raw_input(question + ' [y/n]: ')
            if confirm_flag == 'y':
                print answer
            elif confirm_flag == 'n':
                print 'The user cancel the operation'
                exit()
            else:
                print 'The entry is not valid, please enter y or n.'
        return True

    def run(self):
        """
        run the given command in the command line.
        @return True
        """
        SERVER = self.args.get('sever')
        DB = self.args.get('db')
        PORT = self.args.get('port')
        SRC_PATH = self.args.get('module_path')

        # Static variables (for the moment).
        USER = 'admin'
        PASSWD = 'admin'
        PROTOCOL = 'xmlrpc'
        TIMEOUT = 4000

        oerp = oerplib.OERP(
            server=SERVER, database=DB, protocol=PROTOCOL, port=PORT,
            timeout=TIMEOUT)

        # self.reset_db(oerp, DB, USER, PASSWD)
        self.login_db(oerp, USER, PASSWD)

        dir_names = self.get_modules(SRC_PATH)
        installed_dict = self.install_modules(oerp, dir_names)

        dir_names = installed_dict.keys()
        dir_names.sort()
        dir_names.reverse()

        self.generate_pot_files(oerp, dir_names, SRC_PATH)
        print 'Templating is DONE'

    def commit_new_pot(self, dir_name, SRC_PATH):
        """
        Make a commit with the new Pot File.
        """
        # TODO this need to be configure as an optional option
        commit_msg = '[i18n][%s]' % dir_name
        self.detect_csv(SRC_PATH)

        working_directory = os.getcwd()
        os.chdir(working_directory)

        if self.csv == 'bzr':
            subprocess.call(['bzr', 'add'])
            subprocess.call(['bzr', 'ci', '-m', commit_msg])
        elif self.csv == 'git':
            subprocess.call(['git', 'commit', '-avm', commit_msg])
        else:
            print 'the current module path is not in a csv.' \
                ' The csv actions will not be execute'

    def detect_csv(self, SRC_PATH):
        """
        Detect if the csv is in csv and what type is: bzr or git.
        """
        if os.path.exists(os.path.join(SRC_PATH, '.bzr')):
            csv = 'bzr'
        elif os.path.exists(os.path.join(SRC_PATH, '.git')):
            csv = 'git'
        else:
            csv = False

        if csv:
            os.chdir(SRC_PATH)

        self.csv = csv

    def generate_pot_files(self, oerp, dir_names, SRC_PATH):
        """
        #POT FILES GENERATION
        """
        for dir_name in dir_names:
            directory = '%s/%s' % (SRC_PATH, dir_name)
            if not os.path.exists(directory + '/i18n'):
                new_dir_name = directory + '/i18n'
                os.mkdir(new_dir_name)

            module_ids = oerp.execute(
                'ir.module.module', 'search',
                [('name', '=', dir_name), ('state', '=', 'installed')])
            if not module_ids:
                continue
            lang_wzd_id = oerp.execute(
                'base.language.export', 'create', {
                    'lang': '__new__',
                    'format': 'po',
                    'modules': [(4, dir_names[dir_name])]  # TODO be carefull
                    })
            oerp.execute(
                'base.language.export', 'act_getfile',
                [lang_wzd_id])
            data = oerp.execute(
                'base.language.export', 'read', lang_wzd_id, ['data'])['data']

            file_name = directory + '/i18n/%s.pot' % dir_name
            with open(file_name, 'w') as tt_file:
                tt_file.write(base64.decodestring(data))
            print '[%s] pot_file Generated' % dir_name.upper()
            self.commit_new_pot(dir_name, SRC_PATH)

    def get_modules(self, SRC_PATH):
        """
        Review the module path and return the list of modules inside.
        """
        if not os.path.exists(SRC_PATH):
            print 'Directory not found: ' + SRC_PATH
        dir_names = os.listdir(SRC_PATH)
        dir_names = [dir_name
                     for dir_name in dir_names
                     if not dir_name.startswith('.')]
        # TODO this need to be improve. Need to identify is the current
        # folder is a Odoo module. If not then iterate and get the list of all
        # the Odoo modules.

    def install_modules(self, oerp, dir_names):
        """
        Install modules in the module path.
        """
        module_obj = oerp.get('ir.module.module')
        uninstallable_ids = []
        installed_dict = {}
        installed_dir_names = []
        for dir_name in dir_names:
            module_id = module_obj.search(
                [('name', '=', dir_name), ('state', '!=', 'uninstallable')])
            if module_id:
                installed_module_id = module_obj.search(
                    [('name', '=', dir_name), ('state', '=', 'installed')])
                if not installed_module_id:
                    try:
                        module_obj.button_immediate_install(module_id)
                        installed_dir_names.append(dir_name)
                        print '[%s] installed successfully' % dir_name.upper()
                        installed_dict[dir_name] = module_id[0]
                    except:
                        uninstallable_ids += module_id
                        module_id = module_obj.search(
                            [('state', '=', 'to install')])
                        print '[%s] unmet dependencies' % dir_name.upper()
                        module_obj.button_install_cancel(module_id)
                else:
                    print '[%s] already installed' % dir_name.upper()
                    installed_dir_names.append(dir_name)
                    installed_dict[dir_name] = module_id[0]
            else:
                print '[%s] unavailable to install' % dir_name.upper()
        # TODO print summary with the errors.
        return installed_dict

    def login_db(self, oerp, USER, PASSWD):
        """
        Login into the database
        """
        oerp.login(user=USER, passwd=PASSWD)

    def reset_db(self, oerp, DB, USER, PASSWD):
        """
        Create a new database. If exist then delete the last one and create
        again. Then login and update the module list
        """
        # <WARNING><ACHTUNG><CUIDADO> DROPING PREVIOUS DB
        oerp.db.drop('admin', DB)
        # CREATING A NEW DB
        oerp.db.create_and_wait('admin', DB, demo_data=False)
        oerp.login(user=USER, passwd=PASSWD)
        # UPDATING MODULE LIST
        upd_id = oerp.execute(
            'base.module.update', 'create', {'state': 'init'})
        oerp.execute('base.module.update', 'update_module', upd_id)


def main():
    obj = PotGenerator()
    obj.run()
    return True

if __name__ == '__main__':
    main()
