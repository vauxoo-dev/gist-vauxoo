# -*- encoding: utf-8 -*-
import os
import inflection
import ast
my_path = "/home/jage/instancias/instancias-v7/oml-v2/odoo-mexicov2"
modules_dir = my_path
for dirpath, dnames, fnames in os.walk(modules_dir):
    for f in fnames:
        if f.endswith("__.py"):
            pass
        elif f.endswith(".py"):
            fname = (os.path.join(dirpath, f))
            with open(fname) as fin:
                parsed = ast.parse(fin.read())
            data = []
            with open(fname, 'r') as file:
                data = file.readlines()
                data_ori = list(data)
            class_definitions = [
                node for node in parsed.body if isinstance(node, ast.ClassDef)]
            for cla in class_definitions:
                class_camel = inflection.camelize(
                    cla.name, uppercase_first_letter=True)
                print class_camel
            # need to write the changes to the file
