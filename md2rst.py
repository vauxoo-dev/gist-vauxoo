#!/usr/bin/python
# -*- coding: utf-8 -*-
# PYTHON_ARGCOMPLETE_OK
import argparse
import argcomplete
import os
import subprocess


class MdtoRst(object):

    """
    This script will search for all the README.md files for the
    given path and change it to rst files.'
    """

    epilog = '\n'.join([
        "Odoo Developer Comunity Tool",
        "Development by Katherine Zaoral (github: @zaoral)",
        "Coded by Katherine Zaoral <kathy@vauxoo.com>.",
        "Source code at git:vauxoo-dev/gist-vauxoo."
    ])

    description = """
    This script will search for all the README.md files for the
    given path and change it to rst files.

    NOTE: This script will edit the principal addond path README.md
    so if you want to not please check to remove this change.
    """

    def __init__(self):
        """
        Initialization of the class.
        @return: None
        """
        self.args = self.argument_parser()
        self.path = self.args['path']

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
            prog='md2rst',
            description=self.description,
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog=self.epilog)

        parser.add_argument(
            '--no-confirm',
            action='store_true',
            help=('Ask user for confirmation to the user. Default is True'))

        parser.add_argument(
            '-p', '--path',
            metavar='PATH',
            type=str,
            required=True,
            help=('The module Path you want to apply the transformation'))

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
        files = []
        search_files = ['README.md']
        for sfile in search_files:
            files += subprocess.Popen(
                ['find', self.path, '-name', sfile],
                stdout=subprocess.PIPE).stdout.readlines()
        files.sort()
        files = [item.strip() for item in files]

        module_list = list(set([
            os.path.dirname(fname)
            for fname in files
        ]))

        for module in module_list:
            print 'Module: ' + module
            os.system('cd {path} && git mv README.md README.rst'.format(
                path=module))
        return True


def main():
    obj = MdtoRst()
    obj.run()
    return True

if __name__ == '__main__':
    main()
