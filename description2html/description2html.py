#!/usr/bin/python
# -*- coding: utf-8 -*-
# PYTHON_ARGCOMPLETE_OK
import argparse
import argcomplete
import os
import rst2html
# import BeautifulSoup
import bs4
import subprocess
import pdb


class DescriptionToHtml(object):

    """
    This object pretend to get a addons path and create the index.html files
    for the odoo modules taking the information in the readme.rst
    and __openerp__.py
    """

    epilog = (
        "Odoo Developer Comunity Tool\n"
        "Development by Katherine Zaoral (github: @zaoral)\n"
        "Coded by Katherine Zaoral <kathy@vauxoo.com>.\n"
        "Source code at git:vauxoo-dev/gist-vauxoo.\n")

    description = (
        'This object pretend to get a addons path and create the index.html'
        ' files for the odoo modules taking the information in the readme.rst'
        ' and __openerp__.py'
    )

    def __init__(self):
        """
        Initialization of the class.
        @return: None
        """
        self.args = self.argument_parser()
        self.path = os.path.abspath(self.args['path'])
        self.pretty_option = self.args.get('pretty_style', False)
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
            metavar='path',
            type=str,
            required=True,
            help=('the module path you want to apply the transformation'))

        parser.add_argument(
            '--pretty-style',
            action='store_true',
            help='Create the index.html file using the odoo ccs style. '
                 ' Divide the README titles into visible sections.'
                 ' WARNING: This functionality still beta.')

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
            '__openerp__.py', '__manifest__.py', 'README.rst', 'index.html']
        for sfile in search_files:
            files += subprocess.Popen(
                ['find', root, '-name', sfile],
                stdout=subprocess.PIPE).stdout.readlines()
        files.sort()
        files = [item.strip() for item in files]

        if os.path.isfile(os.path.join(root, '__openerp__.py')) or \
           os.path.isfile(os.path.join(root, '__manifest__.py')):
            module_list = [os.path.basename(root)]
            root = os.path.split(root)[0]
            self.path = root
        else:
            module_list = os.walk(root).next()[1]
            if module_list.count('.git'):
                module_list.remove('.git')
            module_list.sort()

        for module in module_list:
            os.system('echo Generating index.html module ' + module)
            openerp_py = os.path.join(root, module, '__openerp__.py')
            readme_file = os.path.join(root, module, 'README.rst')
            index_file = os.path.join(
                root, module, 'static/description/index.html')

            if openerp_py not in files:
                openerp_py = os.path.join(root, module, '__manifest__.py')
                if openerp_py not in files:
                    not_modules.append(module)
                    continue

            # Get module data
            description = ''
            name, summary, description = self.get_module_data(
                openerp_py, readme_file)

            # Call @nhomar's script.
            html_description = rst2html.html.rst2html(description)

            content = self.prepare_content(html_description, name, summary)

            self.add_missing_dirs(index_file)
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

    def add_missing_dirs(self, index_file):
        """
        Create the static/description folder in the modules.
        @return True
        """
        if not os.path.exists(os.path.dirname(index_file)):
            os.system('echo "  -- Create missing "' + index_file)
            os.makedirs(os.path.dirname(index_file))
        return True

    def prepare_content(self, html_description, name, summary):
        """
        Prepare Content
        """
        try:
            soup = bs4.BeautifulSoup(html_description)
            if summary:
                summary_tag = bs4.Tag(soup, name='h3')
                summary_tag.string = summary
                title_section = soup.findAll('div', attrs={
                    'class': 'section', 'id': name.replace(' ', '-')})
                title_section.insert(2, summary_tag)
            for p_tag in soup.findAll('p'):
                p_tag['class'] = 'oe_mt32'

            for image_tag in soup.findAll('img'):
                image_tag['class'] = 'oe_picture oe_screenshot'

            for tt_tag in soup.findAll('tt'):
                tt_tag.name = 'code'

            for maintainer_section in soup.findAll(id='maintainer'):
                maintainer_section.replaceWith('')

            if not self.pretty_option:
                doc_div = soup.findAll('div', attrs={'class': 'document'})
                if doc_div:
                    doc_div = doc_div[0]
                    doc_div['id'] = 'description'
                    doc_div.name = 'section'
                    doc_div['class'] = 'oe_container'

            # The first h1 is the title.
            title = soup.find('h1')
            if title:
                title.name = 'h2'
                title['class'] = 'oe_slogan'

            flag = True
            for div_section in soup.findAll('div', attrs={'class': 'section'}):
                if self.pretty_option:
                    div_section['class'] = 'section oe_row oe_spaced'
                    section_tag = bs4.Tag(soup, name='section')
                    section_tag['class'] = 'oe_container'
                    if flag:
                        flag = False
                    else:
                        section_tag['class'] = 'oe_container oe_dark'
                        flag = True
                    div_section.wrap(section_tag)
                else:
                    div_section['class'] = 'section oe_span12'

            for table_tag in soup.findAll('table'):
                table_tag['border'] = 0

            # for h2_tag in soup.findall('h2'):
            #     h2_tag.name = 'h3'
            #     h2_tag['class'] = 'oe_slogan'

            if self.pretty_option:
                for h1_tag in soup.findAll('h1'):
                    h1_tag.name = 'h2'
                    h1_tag['class'] = 'oe_slogan'

            head_tag = bs4.Tag(soup, name='head')
            style_tag = bs4.Tag(soup, name='style')
            style_tag.string = '.backgrounds{background-color:#fff;color:#a41d35}'
            head_tag.insert(0, style_tag)
            soup.html.insert(0, head_tag)

            footer_tag = bs4.BeautifulSoup(self.footer)
            soup.body.insert(len(soup.body.contents), footer_tag.html.body.section)
            content = soup.prettify()
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
