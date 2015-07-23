#!/usr/bin/python
# -*- coding: utf-8 -*-
# PYTHON_ARGCOMPLETE_OK
import argparse
import argcomplete
import os
import rst2html
import BeautifulSoup
# import bs4
import subprocess
import pdb


class DescriptionToHtml(object):

    """
    This object pretend to get a addons path and create the index.html files
    for the odoo modules taking the information in the readme.md
    and __openerp__.py
    """

    epilog = (
        "Odoo Developer Comunity Tool\n"
        "Development by Katherine Zaoral (github: @zaoral)\n"
        "Coded by Katherine Zaoral <kathy@vauxoo.com>.\n"
        "Source code at git:vauxoo-dev/gist-vauxoo.\n")

    description = (
        'This object pretend to get a addons path and create the index.html'
        ' files for the odoo modules taking the information in the readme.md'
        ' and __openerp__.py'
    )

    def __init__(self):
        """
        Initialization of the class.
        @return: None
        """
        self.args = self.argument_parser()
        self.path = self.args['path']

        self.get_html_parts()

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
            prog='description2html',
            description=self.description,
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
        not_modules = []
        root = self.path
        files = []
        search_files = [
            '__openerp__.py', 'README.md', 'index.html']
        for sfile in search_files:
            files += subprocess.Popen(
                ['find', root, '-name', sfile],
                stdout=subprocess.PIPE).stdout.readlines()
        files.sort()
        files = [item.strip() for item in files]

        module_list = os.walk(root).next()[1]
        if module_list.count('.git'):
            module_list.remove('.git')
        module_list.sort()

        for module in module_list:
            os.system('echo Generating index.html module ' + module)
            openerp_py = os.path.join(root, module, '__openerp__.py')
            readme_file = os.path.join(root, module, 'README.md')
            index_file = os.path.join(
                root, module, 'static/description/index.html')

            if openerp_py not in files:
                not_modules.append(module)
                continue

            # Get module data
            description = ''
            name, summary, description = self.get_module_data(
                openerp_py, readme_file)

            # Call @nhomar's script.
            html_description = rst2html.html.rst2html(description)

            content = self.prepare_content(html_description, summary)

            self.add_missing_dirs(index_file)
            self.add_missing_footer_logo(module)
            self.add_missing_icon(module)

            with open(index_file, 'w') as ifile:
                ifile.write(content)

        if not_modules:
            for item in not_modules:
                print 'NOTE: This is not an odoo module', item
        return True

    def add_missing_icon(self, module):
        """
        create static/description/icon.png
        @return True
        """
        module_icon = os.path.join(
            self.path, module, 'static/description/icon.png')
        if not os.path.exists(module_icon):
            os.system('cp {src} {dest}'.format(
                src=self.module_icon, dest=module_icon))
        return True

    def add_missing_footer_logo(self, module):
        """
        create static/description/VAUXOO.png
        @return True
        """
        footer_logo = os.path.join(
            self.path, module, 'static/description/VAUXOO.png')
        if not os.path.exists(footer_logo):
            os.system('cp {src} {dest}'.format(
                src=self.footer_logo, dest=footer_logo))
        return True

    def add_missing_dirs(self, index_file):
        """
        Create the static/description folder in the modules.
        @return True
        """
        if not os.path.exists(os.path.dirname(index_file)):
            os.system('echo "  -- Create missing "' + index_file)
            os.makedirs(os.path.dirname(index_file))
        return True

    def prepare_content(self, html_description, summary):
        """
        Prepare Content
        """
        try:
            content = (
                '<section class="oe_container">\n'
                + html_description +
                '</section>\n'
            )
            soup = BeautifulSoup.BeautifulSoup(content)
            if soup.section.div:
                soup.section.div['class'] = 'oe_row oe_spaced'
                del soup.section.div['id']
            if soup.section.div.h1:
                soup.section.div.h1.name = 'h2'
                soup.section.div.h2['class'] = 'oe_slogan'
            if summary:
                summary_tag = BeautifulSoup.Tag(soup, name='h3')
                summary_tag.string = summary
                soup.section.div.insert(2, summary_tag)
            if soup.section.div.p:
                soup.section.div.p['class'] = 'oe_mt32'
                # pdiv_tag = bs4.Tag(soup, name='div')
                # pdiv_tag['class'] = 'oe_span12'
                # soup.section.div.p.wrap(pdiv_tag)
                # pdb.set_trace()
            content = soup.prettify()
            content = self.header + content + self.footer
        except Exception as e:
            pdb.set_trace()
            exit()
        return content

    def get_html_parts(self):
        """
        go to the this package data folder and get the head, template and
        footer.
        """
        script_path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            'data')
        with open(os.path.join(script_path, 'head.html'), 'r') as hfile:
            self.header = hfile.read()
        with open(os.path.join(script_path, 'template.html'), 'r') as hfile:
            self.template = hfile.read()
        with open(os.path.join(script_path, 'footer.html'), 'r') as hfile:
            self.footer = hfile.read()
        self.footer_logo = os.path.join(script_path, 'VAUXOO.png')
        self.module_icon = os.path.join(script_path, 'icon.png')
        return True

    def get_module_data(self, openerp_file, readme_file):
        """
        Get the description of README files and reutrn string
        """
        with open(openerp_file, 'r') as ofile:
            openerp = ofile.read()
        with open(readme_file, 'r') as rfile:
            readme = rfile.read()
        openerp_dict = eval(openerp)
        description = readme
        name = openerp_dict.get('name', '')
        summary = openerp_dict.get('summary', '')
        return name, summary, description


def main():
    obj = DescriptionToHtml()
    obj.run()
    return True

if __name__ == '__main__':
    main()
