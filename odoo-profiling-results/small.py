import sys
import pstats_print2list
from pstats_print2list import print_pstats_list
# print "Method docstring", pstats_print2list.get_pstats_print2list.__doc__
fname = sys.argv[1]
pstats_list = pstats_print2list.get_pstats_print2list([fname], filter_fnames=['/root/'], exclude_fnames=['/root/odoo-8.0'])
print_pstats_list(pstats_list)
