import os
import fileinput
import sys

def replaceAll(file, searchExp, replaceExp="", rm=False):
    for line in fileinput.input(file, inplace=1):
        if (searchExp in line) and rm:
            continue
        if searchExp in line:
            line = line.replace(searchExp,replaceExp)
        sys.stdout.write(line)

for dirpath, dnames, fnames in os.walk("//"):
    for f in fnames:
        if f.endswith(".py"):
            fname = (os.path.join(dirpath, f))
            replaceAll(fname, "import pooler", rm = True)
            replaceAll(fname, "import decimal_precision as dp", "from openerp.addons.decimal_precision import decimal_precision as dp", rm = False)