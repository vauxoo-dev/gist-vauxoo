import os

import gitlab


def get_mr_diff(project_slug='vauxoo/bistro')
    group, project = project_slug.split('/')
    config_file = os.path.expanduser("~/.python-gitlab.cfg")
    gl = gitlab.Gitlab.from_config(group, [config_file])
    project = gl.projects.get(project)
    # print(gl.projects.list())
    # print(project)
    mrs = project.mergerequests.list(state="opened")
    for mr in mrs:
        diffs = mr.diffs.list()
        # print(diffs)
        # print(dir(mr))
        for change in mr.changes()['changes']:
            print(change['diff'])
        # for diff in diffs:
            # print(diff)
            # print(dir(diff))
            # print(diff.list())
            # print(diff.short_print())
            # print(diff.display(True))
        # break
    # print(mrs, len(mrs))
