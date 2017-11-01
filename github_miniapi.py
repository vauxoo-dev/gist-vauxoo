import ast
import sys

import requests
import simplejson


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
        request = self.github_request('users/{owner}/repos?private=true')
        return request

if __name__ == '__main__':
    token = sys.argv[1]
    owner = sys.argv[2]
    # payload = ast.literal_eval(sys.argv[2])
    # repo = sys.argv[4]
    gh_obj = GithubRequest(token, owner=owner)
    print gh_obj.github_get_private_repos()
