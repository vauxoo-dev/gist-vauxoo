import os
import re
pids = [pid for pid in os.listdir('/proc') if pid.isdigit()]

filters = ['static', 'python']

data_pids = []
for pid in pids:
    try:
        data_pid = open(os.path.join('/proc', pid, 'cmdline'), 'rb').read()
        data_pid = data_pid.replace('\x00', ' ')
        if all([filter in data_pid for filter in filters]) == True:
            data_pids.append( data_pid )
    except IOError: # proc has already terminated
        continue

#print data_pids

def get_regex_data(data_pids, regex):
   regex_data_pids = []
   for data_pid in data_pids:
       match_object = re.search(regex, data_pid)
       if match_object:
           #import pdb;pdb.set_trace()
           #match_object.group("branch_base")
           regex_data_pids.append( match_object.groupdict() )
   return regex_data_pids

def get_runbot_process():
    runbot_pid_regex = '([/\w\-_.]*)(build/)(?P<build_name>[\w\-_.]*)(([/\w\-_.]*))'
    regex_data_pids = get_regex_data(data_pids, runbot_pid_regex)
    return list(set( [regex_data_pid['build_name'] for regex_data_pid in regex_data_pids] ))

runbot_process = get_runbot_process()
print runbot_process
print len(runbot_process)
