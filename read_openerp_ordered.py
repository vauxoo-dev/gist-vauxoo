import json
import os
import sys
import ast
import collections
from collections import OrderedDict
import glob

#~ my_path = "/home/jage/base_user_signature_logo/__openerp__.py"
my_path="/home/julio/Documentos/openerp/instancias/7.0/7.0-addons-vauxoo/"

class DictToOrdered(ast.NodeTransformer):
    def visit_Dict(self, node):
        return ast.fix_missing_locations(ast.copy_location(
            ast.Call(
                func=ast.Attribute(
                    value=ast.Name(id='collections', ctx=ast.Load()),
                    attr='OrderedDict',
                    ctx=ast.Load()),
                args=[ast.Tuple(elts=
                        [ast.Tuple(elts=list(pair), ctx=ast.Load())
                         for pair in zip(node.keys, node.values)],
                        ctx=ast.Load())],
                keywords=[],
                starargs=None,
                kwargs=None),
            node))

def parse_dict_as_odict(src):
    parsed = ast.parse(src, '<dynamic>', 'eval')
    transformed = DictToOrdered().visit(parsed)
    compiled = compile(transformed, '<dynamic>', 'eval')
    compiled = eval(compiled)
    return compiled

def dict_key_rename( dict, old_key, new_key ):
    if dict.has_key( old_key):
        if dict.has_key( new_key):
            if isinstance( dict[new_key], list) and isinstance( dict[old_key], list):
                dict[new_key].extend( dict.pop(old_key) )
        else:
            dict[new_key] = dict.pop(old_key) 
    return dict
 
#~ module_dir = sys.argv[1]
#~ for dirpath, dnames, fnames in os.walk(module_dir):
    #~ for f in fnames:
        #~ if f.endswith("__openerp__.py"):
            #~ fname = (os.path.join(dirpath, f))
            #~ replace_all(fname, vale= new_dict_str)
#~ aux = {'init_xml','data'}


#~ modules_dir = my_path
#~ for dirpath, dnames, fnames in os.walk(modules_dir):
    #~ for f in fnames:
        #~ if f.endswith("__openerp__.py"):
            #~ fname = (os.path.join(dirpath, f))
            #~ print fname
            #~ replaceAll(fname, value = {
                #~ 'openerp': ["osv", "tools.translate"],
                #~ "openerp.addons": ["decimal_precision", "report_webkit"],
                #~ "openerp.report":["report_sxw"],
                #~ "rm":["import pooler"],


modules_dir = my_path
for dirpath, dnames, fnames in os.walk(modules_dir):
    for f in fnames:
        if f.endswith("__openerp__.py"):
            fname = (os.path.join(dirpath, f))
            
            with open(fname, 'rb') as fin:
                 dict_str = fin.read()
                 odict = parse_dict_as_odict( dict_str )
                 #odict.rename('init_xml', 'data')
                 odict = dict_key_rename(odict, 'init_xml', 'data')

            new_dict_str = ""
            for line in dict_str.splitlines():
                line = line.strip()
                if line and line[0] == '#':
                    #print line
                    new_dict_str += line + '\n'
                    
            # TODO: is the better way to make??
            # Added the three " in key description, beacuse was removed when dict type OrderedDict
            # Replace \\n by \n because when writting in file not respected \n    
            odict.update({'description': '""{}""'.format(odict.get('description'))})
            odict_str = json.dumps(odict, indent=4)
            odict_str = odict_str.replace('\\n', '\n')
            odict_str = odict_str.replace('\\"', '"')
            
            new_dict_str += odict_str
            f2 = open(fname, 'wb')
            f2.write(new_dict_str)
            f2.close()
