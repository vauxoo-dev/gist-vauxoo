import ast
import sys
 
"""
This script check py file for no get "print" or "pdb" sentence.
"""
 
#file name of file py to check
fname = sys.argv[1]
 
with open(fname) as fin:
    parsed = ast.parse(fin.read())
 
for node in ast.walk(parsed):
    if isinstance(node, ast.Print):
        #if "print" sentence then add a out
        print '"print" at line {} col {}'.format(node.lineno, node.col_offset)
    elif isinstance(node, ast.Import):
        for import_name in node.names:
            if import_name.name == 'pdb':
                #if "print" sentence then add a out
                print '"import pdb" at line {} col {}'.format(node.lineno, node.col_offset)
