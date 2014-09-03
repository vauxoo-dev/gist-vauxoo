"""
#Leer el diccionario en orden
#eval
#transformar las llaves
#guardar diccionario mas comentarios

from collections import OrderedDict

fname = "/Users/moylop260/openerp/instancias/odoo_git_clone/community-addons/odoo-extra/runbot_prebuild/__openerp__.py"
"""
"""
with open(fname, "r") as f:
    print OrderedDict( eval(f.read()) )
"""
"""
import cPickle as pickle
with open(fname, "r") as fp:
    ordered_dict = pickle.load(fp)

print ordered_dict
#OderDict
#eval
#pprint
"""
"""
import re
import ast
import collections

with open(fname) as file:
    line = next(file)
    values = re.search(r"OrderedDict\((.*)\)", line).group(1)
    mydict = collections.OrderedDict(ast.literal_eval(values))
"""
"""
import ast
with open(fname, "r") as file:
    line = next(file)
    print "line", line
"""
"""
import ast

with open(fname) as fin:
    parsed = ast.parse(fin.read())
for node in ast.walk(parsed):
    for body in node.body:
        for value in body.value.values:
            print value.s
"""
"""
with open(fname, 'r') as f:
        s = f.read()
        print OrderedDict(ast.literal_eval(s))
"""
"""
import ast
from collections import OrderedDict

with open(fname) as fin:
    parsed = ast.parse(fin.read())
first_dict = next(node for node in ast.walk(parsed) if isinstance(node, ast.Dict))

keys = []
vals = []
for key in first_dict.keys:
    if isinstance(key, ast.Str):
        keys.append( key.s )
    else:
        keys.append( '' )
    if isinstance(first_dict[key], ast.Str):
        vals.append( first_dict[key].s )
    else:
        vals.append( '' )

#keys = (isinstance(node, ast.Str) and node.s  or '' for node in first_dict.keys )
#vals = (isinstance(node, ast.Str) and node.s or '' for node in first_dict.values  )
#od = OrderedDict(zip(keys, vals))
#print od
print "keys",[keys]
print "vals",[vals]

print "zip(keys, vals)",zip(keys, vals)
"""
"""
import ast
import collections
from collections import OrderedDict
import pprint

fname = "/Users/moylop260/openerp/instancias/odoo_git_clone/community-addons/odoo-extra/runbot_prebuild/__openerp__.py"

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
    return eval(compiled)

with open(fname) as fin:
    dict_str = fin.read()
odict = parse_dict_as_odict( dict_str )
pp = pprint.PrettyPrinter(indent=4)
#print "+++"*10, pp.pprint( odict )

import json

print(json.dumps(odict, indent=4))
# ^nice
"""
"""
def pprint_od(od):
    print "{"
    for key in od:
        #print "%s:%s,\n" % str(key), str(od[key])
        #print " "*4 + "'" + key + "':", od[key]
        #print "%s:%s,"%( pp.pprint(key), pp.pprint(od[key]) )
        #print( key, "", True )# , pp.pprint(od[key])
        print " "*4 + "'%s': %s%s%s,"%( key, isinstance(od[key], str) and "'" or '', od[key], isinstance(od[key], str) and "'" or '' )
        cad = pp.pprint( od[key] )
        print "*"*4 + "[%s]"%(cad)
    print "}"



for key,value in odict.iteritems():
    print key, value

pprint_od( odict )
"""
"""
f=file(fname, "r")
content=f.read().splitlines()

contador=0
diccionario={}
for line in content:
    if contador==0:
        key=line
        diccionario[key]=[]
    else:
        diccionario[key].append(line)
    contador+=1
    if contador==6:
        contador=0

print diccionario
"""


import json
import ast
import collections
from collections import OrderedDict

fname = "/Users/moylop260/openerp/instancias/odoo_git_clone/community-addons/odoo-extra/runbot_prebuild/__openerp__.py"

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
    return eval(compiled)

with open(fname) as fin:
    dict_str = fin.read()
odict = parse_dict_as_odict( dict_str )

new_dict_str = ""
for line in dict_str.splitlines():
    line = line.strip()
    if line and line[0] == '#':
        #print line
        new_dict_str += line + '\n'
odict_str = json.dumps(odict, indent=4)
new_dict_str += odict_str
#print "new_dict_str"
print new_dict_str
