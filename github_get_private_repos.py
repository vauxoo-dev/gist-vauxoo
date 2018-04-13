import ast
import csv
import sys
from StringIO import StringIO
from datetime import datetime

import requests
import simplejson


GITHUB_DT_FORMAT = "%Y-%m-%dT%H:%M:%SZ"

class GithubRequest(object):
    def __init__(self, token, owner=None, repo=None):
        self.token = token
        self.owner = owner or ''
        self.repo = repo or ''
        self.url_base = "https://api.github.com/"

    def github_request(self, url, payload=None):
        url = "%s%s" % (self.url_base, url)
        url = url.format(owner=self.owner, repo=self.repo)
        session = requests.Session()
        session.auth = (token, 'x-oauth-basic')
        session.headers.update({
            'Accept': 'application/vnd.github.she-hulk-preview+json'})
        if payload:
            response = session.post(
                url, data=simplejson.dumps(payload))
        else:
            response = session.get(url)
        response.raise_for_status()
        return response.json()

    def github_get_private_repos(self):
        request = self.github_request('orgs/{owner}/repos?type=private')
        repos = []
        for repo in request:
            pushed_at = datetime.strptime(repo['pushed_at'], GITHUB_DT_FORMAT)
            days = (datetime.now() - pushed_at).days
            repos.append({
                'name': repo['name'],
                'last_days_modified': days,
            })
        return repos

    @staticmethod
    def dicts2csv(datas):
        if not datas:
            return
        csv_file = StringIO()
        csv_obj = csv.DictWriter(csv_file, datas[0].keys())
        csv_obj.writeheader()
        csv_obj.writerows(datas)
        csv_file.seek(0)
        return csv_file.read()


if __name__ == '__main__':
    token = sys.argv[1]
    owner = sys.argv[2]
    # payload = ast.literal_eval(sys.argv[2])
    # repo = sys.argv[4]
    gh_obj = GithubRequest(token, owner=owner)
    repos = gh_obj.github_get_private_repos()
    csv_str = GithubRequest.dicts2csv(repos)
    print csv_str
