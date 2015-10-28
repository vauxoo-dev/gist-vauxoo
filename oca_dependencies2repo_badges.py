
import os
import re

# Set BRANCH and TOKEN environment variables and set in this path the oca_dependencies.txt file

travis_private_badge = ("[![Build Status](https://magnum.travis-ci.com/"
    "{owner}/{repo}"
    ".svg?token="
    "{token}&branch={branch}"
    ")](https://magnum.travis-ci.com/"
    "{owner}/{repo})"
)
travis_public_badge = ("[![Build Status](https://travis-ci.org/"
    "{owner}/{repo}"
    ".svg?branch={branch})](https://travis-ci.org/"
    "{owner}/{repo})"
)


print "# CI Status of repository dependencies"
print "| Repo | Travis |\n| --- | --- |"
with open("oca_dependencies.txt", "r") as frepos:
    for line in frepos:
        repo = line.strip('\n').split(' ')[1]
        regex = "(?P<host>(git@|https://)([\w\.@]+)(/|:))(?P<owner>[~\w,\-,\_]+)/(?P<repo>[\w,\-,\_]+)(.git){0,1}((/){0,1})"
        match_object = re.search(regex, repo)
        if match_object:
            data = {
                'owner': match_object.group("owner"),
                'repo': match_object.group("repo"),
                'host': match_object.group("host"),
                'branch': os.environ['BRANCH'],
                'token': os.environ['TOKEN'],
            }
            print '| ' + repo + ' |',
            if data['host'].startswith('git@github.com:'):
                print travis_private_badge.format(**data),
            if data['host'].startswith('https://github.com/'):
                print travis_public_badge.format(**data),
            print '|'
