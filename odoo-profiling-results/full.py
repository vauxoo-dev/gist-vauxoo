#!/usr/bin/python
import sys
from pstats_print2list import get_pstats_print2list, print_pstats_list
fname_stats = sys.argv[1]
pstats_list = get_pstats_print2list(
    fname_stats,
    filter_fnames=['myfile1.py', 'myfile2.py', 'root_path1'],
    exclude_fnames=['dontshow.py', 'path_dont_show'],
    sort='cumulative',
    limit=5,
)
print_pstats_list(pstats_list)
