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
        "Source code at git@github.com:vauxoo-dev/gist-vauxoo\n\n"
        "Contributors:\n"
        " - Saul Gonzalez <saul@vauxoo.com>\n"
        " - Humberto Arocha <hbto@vauxoo.com> (github@hbto)\n"
        " - Katherine Zaoral <kathy@vauxoo.com> (github@zaoral)\n\n")

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
            default='8069',
            help='Port to use to connect to the database')

        parser.add_argument(
            'module-path',
            metavar='MODULE PATH',
            type=str,
            help='The module path')

        parser.add_argument(
            '--version',
            action='version',
            version='%(prog)s 8.0.2.0.0')

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
        SERVER = self.args.get('server')
        DB = self.args.get('db')
        PORT = self.args.get('port')

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

        modules_data = self.get_modules()
        modules_data = self.install_modules(oerp, modules_data)
        self.generate_pot_files(oerp, modules_data)
        print '\nTemplating is DONE\n'

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

    def generate_pot_files(self, oerp, modules_data):
        """
        #POT FILES GENERATION
        """
        print "\n>> Generationg POT files ...\n"
        ordered_module_list = sorted(modules_data.keys())
        for module_name in ordered_module_list:
            module_attr = modules_data.get(module_name)
            module_path = module_attr.get('path')
            i18n_folder = os.path.join(module_path, 'i18n')
            if not os.path.exists(i18n_folder):
                os.mkdir(i18n_folder)
            module_id = module_attr.get('id')
            lang_wzd_id = oerp.execute(
                'base.language.export', 'create', {
                    'lang': '__new__',
                    'format': 'po',
                    'modules': [(4, module_id)],
                })
            oerp.execute(
                'base.language.export', 'act_getfile',
                [lang_wzd_id])
            data = oerp.execute(
                'base.language.export', 'read', lang_wzd_id, ['data'])['data']

            # Write pot file
            file_name = os.path.join(i18n_folder, module_name + '.pot')
            with open(file_name, 'w') as tt_file:
                tt_file.write(base64.decodestring(data))
            print 'module %s' % module_name

            # self.commit_new_pot(module_name, module_path)

    def get_modules(self):
        """
        Review the module path and return the list of modules inside.
        """
        print "\n>> Finding Odoo modules\n"
        SRC_PATH = self.args.get('module-path')
        if not os.path.exists(SRC_PATH):
            print 'Directory not found: ' + SRC_PATH
            exit()

        # Find modules
        openerp_py = subprocess.Popen(
            ['find', SRC_PATH, '-name', '__openerp__.py'],
            stdout=subprocess.PIPE).stdout.readlines()

        if not openerp_py:
            print 'There is not modules in the given path'
            exit()
        else:
            openerp_py = [item.strip() for item in openerp_py]
            modules_data = {}
            for item in openerp_py:
                module_path = os.path.split(item)[0]
                modules_data.update({
                    os.path.basename(module_path): {
                        'path': module_path}
                })
            ordered_module_list = sorted(modules_data.keys())
            for module_name in ordered_module_list:
                print 'module ' + module_name
        return modules_data

    def install_modules(self, oerp, modules_data):
        """
        Install modules in the module path.
        """
        print "\n>> Installing Modules ...\n"
        module_obj = oerp.get('ir.module.module')
        uninstallable_ids = []
        installed_dir_names = []
        for module in modules_data.keys():
            module_id = module_obj.search(
                [('name', '=', module), ('state', '!=', 'uninstallable')])
            if module_id:
                installed_module_id = module_obj.search(
                    [('name', '=', module), ('state', '=', 'installed')])
                if not installed_module_id:
                    try:
                        module_obj.button_immediate_install(module_id)
                        installed_dir_names.append(module)
                        print '[%s] installed successfully' % module
                    except:
                        uninstallable_ids += module_id
                        module_id = module_obj.search(
                            [('state', '=', 'to install')])
                        print '[%s] unmet dependencies' % module
                        module_obj.button_install_cancel(module_id)
                        modules_data.pop(module)
                else:
                    installed_dir_names.append(module)
                modules_data.get(module).update({'id': module_id[0]})
            else:
                print '[%s] unavailable to install' % module
                modules_data.pop(module)
        # TODO print summary with the errors.
        return modules_data

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
