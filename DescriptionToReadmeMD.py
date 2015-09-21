#!/usr/bin/python
# -*- encoding: utf-8 -*-
# PYTHON_ARGCOMPLETE_OK
import argparse
import argcomplete
import os
import re
import pprint


class DescriptionToMarkdown(object):

    """
    This object pretend to get an odoo addons path and move the openerp.py
    descriptions to a README.md file.
    """

    epilog = '\n'.join([
        'Odoo Developer Comunity Tool',
        'Developed by:',
        '    Sergio Tostado <sergio@vauxoo.com>'
        ' <github.com/sergioernestotostadosanchez>',
        '    Katherine Zaoral <kathy@vauxoo.com> <github.com/zaoral>\n',
        'Source code at git:vauxoo-dev/gist-vauxoo.',
        ' '
    ])

    description = '\n'.join([
        'Move the description from __openerp__.py to a README.md file.\n',
        'NOTE: Please review the README.md files to make sure they work',
        '      propertly before commit',
    ])

    def __init__(self):
        """
        Initialization of the class.
        @return: None
        """
        self.args = self.argument_parser()
        self.project_path = self.path = self.args['path']
        self.module_declaration_files = []
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
            prog='description2md',
            formatter_class=argparse.RawTextHelpFormatter,
            description=self.description,
            epilog=self.epilog)

        parser.add_argument(
            '--no-confirm',
            action='store_true',
            help=('Do not ask user for confirmation before run the script.'
                  '\nDefault is True'))

        parser.add_argument(
            '-p', '--path',
            metavar='PATH',
            type=str,
            required=True,
            help='The addons module path were you want to apply the'
                 '\ntransformation.')

        argcomplete.autocomplete(parser)
        return parser.parse_args().__dict__

    def confirm_run(self, args):
        """
        Manual confirmation before runing the script. Very usefull.
        @param args: dictionary of arguments.
        @return True or exit the program in the confirm is no.
        """
        pprint.pprint('\n... Configuration of Parameters Set')
        for (parameter, value) in args.iteritems():
            pprint.pprint('%s = %s' % (parameter, value))

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
                pprint.pprint(answer)
            elif confirm_flag == 'n':
                pprint.pprint('The user cancel the operation')
                exit()
            else:
                pprint.pprint('The entry is not valid, please enter y or n.')
        return True

    def run(self):
        """
        run the given command in the command line.
        @return True
        """
        self.get_all_openerp_files_in_project()
        self.get_description_to_readme_file()
        return True

    def get_all_openerp_files_in_project(self):
        for root, dirnames, filenames in os.walk(self.project_path):
            dirnames = dirnames
            for filename in filenames:
                if filename == '__openerp__.py':
                    self.module_declaration_files.append(
                        "%s/%s" % (root, filename))

    def get_description_to_readme_file(self):
        pprint.pprint(
            "Getting description and creating README.md for %s modules" %
            len(self.module_declaration_files))
        for m_file in self.module_declaration_files:
            pprint.pprint("File: %s ..." % m_file)
            with open(m_file, 'r') as openerpfile:
                file_string = openerpfile.read()
                openerp_dict = eval(file_string)
                description = openerp_dict.get(
                    'description', '\nTODO: Add module description')
            try:
                pattern = ''.join([
                    r"(?P<base>[\"']{key}[\"']\s*:\s*)".format(
                        key='description'),
                    "(?P<init>[\"']{3,3})",
                    re.escape(description),
                    r"(?P<end>[\"']{3,3}[\s\n]*,[\s\n]*)"
                ])
                rp = re.compile(pattern)
                new_openerp_content = rp.sub('', file_string)

                with open(m_file, 'w') as openerpfile:
                    openerpfile.write(new_openerp_content)

                # create readme file
                self.create_readme_md(openerp_dict, m_file)
            except Exception as e:
                pprint.pprint("ERROR: %s ..." % m_file)
                pprint.pprint(e)

    def create_readme_md(self, openerp_dict, m_file):
        """
        Create README.md file with the data extract from the openerp descriptor
        file.

         - Read the openerp descriptor and find the module name, If there is
           not module name defined then return the module folder as the module
           name.

        @return True
        """
        module_name = openerp_dict.get('name', os.path.dirname(m_file))
        description = openerp_dict.get('description',
                                       'This module has not description')
        description = '\n'.join([
            item.rstrip()
            for item in description.splitlines()
        ])

        content = '{name}\n{title}\n\n{description}'.format(
            name=module_name,
            title="=" * len(module_name),
            description=description)
        if not (os.path.isfile(os.path.dirname(m_file)+'/README.md' or
                os.path.dirname(m_file)+'/readme.md')):
            path = os.path.join(os.path.dirname(m_file), 'README.md')
            with open(path, 'w') as readmefile:
                readmefile.write(content)
        return True


def main():
    obj = DescriptionToMarkdown()
    obj.run()
    return True

if __name__ == '__main__':
    main()
