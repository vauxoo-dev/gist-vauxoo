import csv
import hashlib

from datetime import datetime
from collections import OrderedDict, defaultdict


def clear_cache_stats(fname):
    with open(fname) as csvf:
        csvo = csv.DictReader(csvf)
        stats = {}
        for row in csvo:
            tcbk_str = row['message'].split('odoo.models.clear_caches: ')[1].strip().replace('\\\\n', '\n')
            tcbk_lines = tcbk_str.splitlines()[-7:]
            tcbk_str = '\n'.join(tcbk_lines)
            model = tcbk_lines[0].split(' ')[0]
            tcbk_md5 = hashlib.md5(tcbk_str.encode('UTF-8')).hexdigest()
            key = tcbk_md5
            dt = datetime.strptime(row['timestamp'].split('.')[0], '%Y-%m-%dT%H:%M:%S')
            if key not in stats:
                stats[key] = {
                    'count': 1,
                    'tcbk': tcbk_str,
                    'dates': [dt],
                    'model': model,
                }
            else:
                stats[key]['count'] += 1
                stats[key]['dates'].append(dt)
    def dates_diff(dates, work_dict, max_min=3):
        dates.sort()
        work_dict['dates_diff_min'] = []
        dt_last = None
        for date in dates:
            dt_diff = int((date - dt_last).seconds/60) if dt_last is not None else 0
            dt_last = date
            if dt_last is not None and dt_diff <= max_min:
                continue
            work_dict['dates_diff_min'].append(dt_diff)
        work_dict['dates_count'] = len(work_dict['dates_diff_min'])
    for key, values in stats.items():
        dates_diff(values['dates'], values)
    counter_ordered = OrderedDict(sorted(stats.items(), key=lambda item: item[1]['dates_count'], reverse=True))
    limit = 2
    for count, value in enumerate(counter_ordered.values()):
        if count > limit:
            break
        print("Occurrences %(dates_count)d model: %(model)s. dates_diff %(dates_diff_min)s\n\n%(tcbk)s\n" % value)



if __name__ == '__main__':
    # fname = '/Volumes/sand2tb/Downloads/graylog-search-result-relative-86400.csv'
    fname = '/Volumes/sand2tb/Downloads/graylog-search-result-relative-172800 (1).csv'
    clear_cache_stats(fname)
# counter = defaultdict(int)
# dates = []
# fname = "graylog-search-result-relative-432000.csv"
# fname = "graylog-search-result-relative-432000 (1).csv"
# dt_last = None
# with open(fname) as csvf:
#     csvo = csv.DictReader(csvf)
#     for row in csvo:
#         msg = row['message'].split('price_clear_cache_mixin: ')[1].strip()
#         # msg = row['message'].split('clear_caches: ')[1].strip()
#         # if 'load_modules' in msg or 'clean_attachments' in msg:
#         #     continue
#         # model = msg.split(' ')[0]
#         model = msg.split(':')[-1]
#         # counter[model] += 1
#         dt = datetime.strptime(row['timestamp'].split('.')[0], '%Y-%m-%dT%H:%M:%S')
#         # dt_diff = (dt - dt_last).seconds if dt_last is not None else 0
#         # print(dt, dt_last, dt_diff)
#         # if dt_diff >= 1:
#             # continue
#         dates.append(dt)
#         # counter[dt.strftime('%Y-%m-%d %H:%M')]
#         # counter[dt.strftime('%Y-%m-%d %H:%M')] = dt_diff
#         # date = .strptime()
#         # dt_last = dt
# dates.sort()
# minutes = []
# for date in dates:
#     dt_diff = int((date - dt_last).seconds/60) if dt_last is not None else 0
#     if dt_diff > 3:
#         minutes.append(dt_diff)
#         print(date, dt_last, dt_diff)
#     dt_last = date
# # import pdb;pdb.set_trace()
# print((sum(minutes) - max(minutes) - min(minutes)) / (len(minutes) - 2))
# # print(sorted(counter.items(), key=lambda item: item[1], reverse=True))
# # print(sorted(counter.keys()))
# # print(sorted(counter.items(), key=lambda item: item[0]))
