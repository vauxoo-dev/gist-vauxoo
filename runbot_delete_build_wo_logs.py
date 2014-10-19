import shutil
import os
import sys
builds_path = sys.argv[1]

for build_path in os.listdir(builds_path):
 if os.path.isdir(build_path):
  for item in os.listdir(build_path):
    path_item = os.path.join(build_path, item)
    #import pdb;pdb.set_trace()
    if os.path.isdir( path_item ):
        if item != 'logs':
            shutil.rmtree( path_item )
        elif os.path.isfile( path_item ):
            os.remove( path_item )
