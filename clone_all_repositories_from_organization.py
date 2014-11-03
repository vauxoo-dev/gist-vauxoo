from github import Github


github_login = raw_input("Login: ")
github_password = raw_input("Password: ")
github_organization = raw_input("Organization: ")
g = Github(github_login, github_password)
#import pdb;pdb.set_trace()
github_org = g.get_organization("oca")
github_repos = github_org.get_repos()
print 'mkdir "%s"'%( github_organization )
for repo in github_repos:
    print 'cd "%s"'%( github_organization )
    print 'git clone "%s"'%( repo.git_url )
    print 'cd ..'
