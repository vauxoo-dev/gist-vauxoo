# -*- encoding: utf-8 -*-

import fnmatch
import os


class DescriptionToReadmeMD:
    
    def __init__(self, path):
        self.project_path = path
        self.module_declaration_files = []
    
    def get_all_openerp_files_in_project(self):
        for root, dirnames, filenames in os.walk(self.project_path):
            for filename in fnmatch.filter(filenames, '*.*'):
                if filename == '__openerp__.py':
                    self.module_declaration_files.append("%s/%s" % (root, filename))
    
    def get_description_to_readme_file(self):
        print "Getting description and creating README.md for %s modules" % len(self.module_declaration_files)
        for m_file in self.module_declaration_files:
            print "File: %s ..." % m_file
            description = ""
            start_description_index = 0
            start_delete_index = 0
            final_description_index = 0
            final_delete_index = 0
            module_name = ""
            new_openerp_content = ""
            file_string = open(m_file, 'r').read()
            # Getting description and new content for __openerp__.py file
            if "description" in file_string:
                start_description_index = file_string.find('description')
                start_delete_index = start_description_index - 1
                start_description_index += file_string[start_description_index:].find('"""') + 3
                final_description_index = start_description_index + file_string[start_description_index:].find('"""') - 1
                final_delete_index = final_description_index + file_string[final_description_index+4:].find('"') + 4
                new_openerp_content = file_string.replace(file_string[start_delete_index:final_delete_index], '')
                description = file_string[start_description_index:final_description_index]
                module_name = m_file[:m_file.rfind('/')]
                module_name = module_name[module_name.rfind('/') + 1:]
                description = "%s\n%s\n%s" % \
                    (module_name,
                     "=" * len(module_name),
                     description.replace('=',''))
                # Creating README.md file and overwritting __openerp__.py file
                new_readme_file = open('%sREADME.md' % m_file[:m_file.rfind('/') + 1], 'w')
                new_readme_file.write(description)
                new_readme_file.close()
                new_openerp_file = open(m_file, 'w')
                new_openerp_file.write(new_openerp_content)
                new_openerp_file.close()
                
                

obj = DescriptionToReadmeMD('/home/sergio/Documentos/VAUXOO/odoo/my_dev_branches/8.0-add-readmes-to-module-2783')
obj.get_all_openerp_files_in_project()
obj.get_description_to_readme_file()
