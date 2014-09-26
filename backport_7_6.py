import os
import fileinput
import sys
import ast
from xml.dom import minidom
from lxml import etree
import xml.etree.ElementTree as ET
import meta
path = "/home/ernesto/instancias/gbw_replica_prod/addons_all/test_modules/l10n_mx_company_multi_address"

def _get_paths_py_to_test(path):
    """
    This method is used to search py files in the path.

    :param path: Path of search py files.
    """
    list_paths_py = {"py": [], "xml": []}
    for dirname, dirnames, filenames in os.walk(path):
        for filename in filenames:
            fname_path = os.path.join(dirname, filename)
            fext = os.path.splitext(fname_path)[1]
            if fext == '.py':
                list_paths_py.get('py', []).append(fname_path)
            elif fext == '.xml':
                list_paths_py.get('xml', []).append(fname_path)
            else:
                continue
    return list_paths_py

list_paths = _get_paths_py_to_test(path)

def replace_imports(paths):
    dic = {'from openerp.osv import fields, osv': 'from osv import fields, osv', 
            'from openerp.tools.translate import _': 'from tools.translate import _',
            'from openerp import pooler, tools': 'import pooler, tools',
            'osv.Model': 'osv.osv'}
    
    for path in paths.get('py', []):
        #~ f1 = open(path, 'r')
        #~ text = f1.read()
        #~ f1.close()
        #~ fname = sys.argv[1]
        dict_to_write = {}
        with open(path) as fin:
            parsed = ast.parse(fin.read())
        data = []
        with open(path, 'r') as file:
            data = file.readlines()
            data_ori = list(data)
        for node in ast.walk(parsed):
            # Checks for imports with openerp
            if isinstance(node, ast.ImportFrom):
                print node.__dict__, 'FFFFFFFFFFFFF'
                if node.__dict__.get('module') and 'openerp' in node.__dict__.get('module'):
                    #Check from openerp import algo replace for import algo
                    if 'openerp' == node.__dict__.get('module'):
                        from_import_replace = "import {}\n".format(", ".join([name.name for name in node.__dict__.get('names')]))
                        data[node.__dict__.get("lineno")-1] = from_import_replace
                        print from_import_replace, 'impt_line_replaceimpt_line_replaceimpt_line_replaceimpt_line_replaceimpt_line_replace'
                    #Check import openerp.algo1, openerp.algo2 and remove openerp
                    else:
                        import_replace = "from {} import {}\n".format(node.__dict__.get('module').replace("openerp.", ''), ", ".join([name.name for name in node.__dict__.get('names')]))
                        data[node.__dict__.get("lineno")-1] = import_replace
                        print import_replace, 'OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO'
            if hasattr(node, 'body') and isinstance(node.body, list):
                assigns = [x for x in node.body if type(x) == ast.Assign]
                clases = [x for x in node.body if type(x) == ast.ClassDef]
                print path, 'CLASSSSSSSSSSSSSSSSSSSSSSSSSS', clases
                #to check attribute Model in class
                for clase in clases:
                    for att in clase.__dict__.get("bases"):
                        print att.__dict__, '$$$$$$$$$$$$$$$'
                        if att.__dict__.get("attr") and att.__dict__.get("attr") == "Model":
                            class_attr = "class {}(osv.{}):\n".format(clase.__dict__.get("name"), att.__dict__.get("attr").replace("Model", "osv"))
                            print class_attr, clase.__dict__.get("lineno")-1, '#####################'
                            data[clase.__dict__.get("lineno")-1] = class_attr
                    if len(clases) == 1:
                        term_class = "{}()\n".format(clase.__dict__.get("name"))
                        data.append(term_class)
                    else:
                        if clases.index(clase) < len(clases)-1:
                            before_line = clases[clases.index(clase)+1].__dict__.get('lineno')-2
                            term_class = "{}()\n".format(clase.__dict__.get("name"))
                            data.insert(before_line, term_class)
                            print data[before_line-1],data[before_line], data[before_line+1], "&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&"
                        elif clases.index(clase) == len(clases)-1:
                            term_class = "{}()\n".format(clase.__dict__.get("name"))
                            data.append(term_class)
                            print data[len(data)-1], "&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&"
                for assign in assigns:
                    vars_node = [ name_var.id for name_var in assign.targets if type(name_var) == ast.Name]
                    print vars_node
                    #check to _name var with "_"
                    if '_name' in vars_node:
                        print assign.__dict__, 'FFFFFFFFFFFFFFFFFFFFf', assign.targets[0].id
                        dict_test = assign.__dict__.get('value').__dict__
                        name_of_class = "{}{} = '{}'\n".format(" "*assign.__dict__.get("col_offset"), assign.targets[0].id,dict_test.get("s").replace('_', '.'))
                        data[assign.__dict__.get("lineno")-1] = name_of_class
                        print data[assign.__dict__.get("lineno")-1], "DATAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
                    if '_columns' in vars_node:
                        dict_test = assign.__dict__.get('value').__dict__
                        if dict_test.get('keys', False) and dict_test.get('values', []):
                            for field in dict_test.get('values', []):
                                if field.__dict__.get("func", False):
                                    if field.__dict__.get("func").__dict__.get("attr", False) == "char":
                                        args_field = [hola.arg for hola in field.__dict__.get("keywords", [])]
                                        if not 'size' in args_field:
                                            list_args = []
                                            list_args = ["'{}'".format(arg.__dict__.get("s")) for arg in field.__dict__.get("args")]
                                            for keyword in field.__dict__.get("keywords"):
                                                arg_str = ""
                                                dict_types = {ast.Str: 's', ast.Num: "n", ast.Name: "id"}
                                                if type(keyword.__dict__.get("value")) == ast.Str:
                                                #~ print "{} = '{}'".format(keyword.__dict__.get("arg"), keyword.__dict__.get("value").__dict__.get(dict_types.get(type(keyword.__dict__.get("value")))))
                                                    arg_str = "{} = '{}'".format(keyword.__dict__.get("arg"), keyword.__dict__.get("value").__dict__.get(dict_types.get(type(keyword.__dict__.get("value")))))
                                                else:
                                                    arg_str = "{} = {}".format(keyword.__dict__.get("arg"), keyword.__dict__.get("value").__dict__.get(dict_types.get(type(keyword.__dict__.get("value")))))
                                                list_args.append(arg_str)
                                            list_args.append("size=64")
                                            pre_format_field = "'{}': fields.char({}),".format(dict_test.get('keys')[dict_test.get('values', []).index(field)].__dict__.get("s"), ", ".join(list_args))
                                            print dict_test.get('keys')[dict_test.get('values', []).index(field)].__dict__, 'YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY'
                                            data[field.__dict__.get("lineno")-1] = "{}{}\n".format(" "*dict_test.get('keys')[dict_test.get('values', []).index(field)].__dict__.get("col_offset"), pre_format_field)
                                            #~ print data[field.__dict__.get("lineno")-1], 'HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH'
                                            #~ print path, field.__dict__, 'DICTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT'
        if data != data_ori:
            with open(path, 'w') as file:
                file.writelines( data )
    for path in paths.get('xml', []):
        f=open(path, 'r')
        parser = etree.XMLParser(remove_blank_text=True)
        tree = ET.parse(f, parser)
        f.close()
        print tree.getroot()
        read = tree.findall("./data/record")
        print read, 'READDDDDDDDDDDDDDDDDD'
        for record in read:
            types =  record.findall('field')
            list_fields = [data.get('name') for data in types]
            print record.get('id', False), 'EEEEEEEEEEEEEEEEE'
            if not 'type' in list_fields and 'model' in list_fields:
                if 'arch' in list_fields:
                    pos = list_fields.index('arch')
                    x = etree.Element('field')
                    if types[pos].findall('./form'):
                        form_node = types[pos].findall('./form')
                        x.text = "form"
                        form_node[0].attrib.pop('version')
                        if form_node[0].findall('./sheet'):
                            sheet_nodes = list(form_node[0].findall('./sheet')[0])
                            form_node[0].remove(form_node[0].findall('./sheet')[0])
                            import pdb;pdb.set_trace()
                            for node in sheet_nodes:
                                print node, 'NODEEEEEEEEEEEEEEEEE'
                                form_node[0].insert(0, node)
                                #~ form_node.append(node)
                            print "DESPUESSSSSSSSSSSSs", form_node[0].items()
                    elif types[pos].findall('./tree'):
                         x.text = "tree"
                    elif types[pos].findall('./search'):
                        x.text = "search"
                    else:
                        continue
                    x.set('name', 'type')
                    record.insert(0, x)
        #~ print minidom.parseString(ET.tostring(tree.getroot())).toprettyxml(indent="    ").encode('ascii', 'xmlcharrefreplace')
        with open(path, 'w') as out:
            doc_xml = minidom.parseString(ET.tostring(tree.getroot())).toprettyxml(indent="    ").encode('ascii', 'xmlcharrefreplace')
            out.write(doc_xml)

replace_imports(list_paths)
