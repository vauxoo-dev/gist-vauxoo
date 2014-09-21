import os
pids = [pid for pid in os.listdir('/proc') if pid.isdigit()]

filters = ['static', 'python']

data_pids = []
for pid in pids:
    try:
        data_pid = open(os.path.join('/proc', pid, 'cmdline'), 'rb').read()
        if all([filter in data_pid for filter in filters]) == True:
            data_pids.append( data_pid )
    except IOError: # proc has already terminated
        continue

print data_pids
