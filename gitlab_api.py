import os

import gitlab


if __name__ == '__main__':
    config_file = os.path.expanduser("~/.python-gitlab.cfg")
    gl = gitlab.Gitlab.from_config('vauxoo', [config_file])
    project = gl.projects.get("vauxoo/bistro")
    # print(gl.projects.list())
    # print(project)
    mrs = project.mergerequests.list(state="opened")
    for mr in mrs:
        diffs = mr.diffs.list()
        # print(len(diffs))
        # print(mr)
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
