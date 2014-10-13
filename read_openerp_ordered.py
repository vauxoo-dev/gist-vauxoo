##!/usr/bin/python
# -*- encoding: utf-8 -*-
import json
import os
import sys
import ast
import collections
from collections import OrderedDict
import glob
import codecs
from heapq import merge
import fileinput

#~ my_path = "/home/jage/base_user_signature_logo/__openerp__.py"
my_path="/home/jage/pruebas-encode/trunk/l10n_ve_fiscal_book"

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
    #print src
    transformed = DictToOrdered().visit(parsed)
    compiled = compile(transformed, '<dynamic>', 'eval')
    compiled = eval(compiled)
    #print compiled
    return compiled

def dict_key_rename( dict, old_key, new_key ):
    if dict.has_key( old_key):
        if dict.has_key( new_key):
            if isinstance( dict[new_key], list) and isinstance( dict[old_key], list):
                dict[new_key].extend( dict.pop(old_key) )
            else:
                print "This tried to rename a key that already exists that can make conflicts, do it manually"
        else:
            dict[new_key] = dict.pop(old_key) 
    return dict

modules_dir = my_path
for dirpath, dnames, fnames in os.walk(modules_dir):
    for f in fnames:
        if f.endswith("__openerp__.py"):
            fname = (os.path.join(dirpath, f))
            print fname
            with codecs.open(fname, 'r3', encoding='utf-8') as fin:
                 dict_str = fin.read()
                 #print dict_str
                 contador = 0
                 with open(fname,"r") as f:
                     for line in f.readlines():
                         contador+= 1
                         if '""",' in line:
                            #print contador
                             num=int(contador)
                             #print num
                 f.close
                 with open(fname,"r") as f:
                     #lista = []
                     comments_list = [line for line in f.readlines()[num:] if '#' in line]
                     for i in comments_list:
						 if i == "# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:":
							 comments_list.remove(i)
							 print comments_list
                     comentarios= "".join(comments_list)
                  
                   
                 f.close()
                 #print dict_str
                 odict = parse_dict_as_odict( dict_str.encode('utf8') )
                 des = odict.get('description')
                 description=[des]
                 #print type(description)
                 description.append(comentarios + '\n')
                 cadena = "".join(description)
                 
                 odict = dict_key_rename(odict, 'init_xml', 'data')
                 odict= dict_key_rename(odict, 'demo_xml', 'demo')
                 odict = dict_key_rename(odict, 'update_xml', 'data')
                 odict = dict_key_rename(odict, 'active', 'auto_install')
                
           
                 
                 #del odict['update_xml']

            bandera = False
            new_dict_str = ""
            for line in dict_str.splitlines():
                line = line.strip()
                if line and line[0]=="{":
                    bandera= True
                if line and line[0] == '#' and bandera == False:
                    #print line
                    new_dict_str += line + '\n'
                    #print new_dict_str
                    
            # TODO: is the better way to make??
            # Added the three " in key description, beacuse was removed when dict type OrderedDict
            # Replace \\n by \n because when writting in file not respected \n 
            
            lista=[("name", ""),
                    ("version", ""),
                    ("author", ""),
                    ("category", ""),
                    ("description", ""),
                    ("website", ""), 
                    ("license", ""),
                    ("depends", []),
                    ("demo", []),
                    ("data", []),
                    ("test", []),
                    ("js", []),
                    ("css", []),
                    ("qweb", []),
                    ("installable", True),
                    ("auto_install", None )]
                    #("active", False)]
                    
            
            olist= OrderedDict((i_key, odict.get(i_key, i_default)) for i_key, i_default in lista)
            olist.update({'description':cadena})
            olist.update({'description': '""{}""'.format(olist.get('description'))})
            #import pdb; pdb.set_trace()
            odict_str = json.dumps(olist, ensure_ascii=False, indent=4, encoding="utf-8")
            odict_str = odict_str.replace('\\n', '\n')
            odict_str = odict_str.replace('\\"', '"')
            #import pdb; pdb.set_trace()
            
            odict_str = odict_str.replace('true', 'True').replace('false', 'False')
        
            new_dict_str += odict_str.decode('utf8')
            f2 = codecs.open(fname, 'wb', encoding='utf-8')
            f2.write(new_dict_str)
       
            f2.close()
              
            with open(fname, 'r') as f:
                lines = [line for line in f.readlines() if not line.replace(' ','').lower().startswith("#vim:expandtab:")]
            f.close()
            with open(fname, 'w') as f:
                f.writelines(lines)
                #print lines
            f.close
            
            
            for line in fileinput.input(fname, inplace=True):
                print line.rstrip()
                
                
            for line in fileinput.input(fname, inplace=True):
            	if line.startswith('\t'):
            		print (line.replace('\t',"    ")).rstrip('\n')
		else:
			print(line.replace('\n', '')) 
					
            f2 = open(fname,"a")
            f2.write("# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:" + '\n')
            f2.close
