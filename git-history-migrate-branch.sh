#!/bin/bash

# In order for this script to work you must:
# - have git installed
# - have hub installed
# - configure your hub config file like:
# ~/.config/hub

# github.com:
# - user: USER
#   oauth_token: TOKEN
#   protocol: https

# TOKEN must be created in github / setting / Personal Access Tokens

while IFS='' read -r module || [[ -n "$module" ]]; do
    echo "Module: $module"

    echo "Moving inside xDev Folder"
    cd ~/xDev/git

    echo "Copying addons-vauxoo"
    cp -r addons-vauxoo cp_src
    echo "Moving inside cp_src to migrate $module"
    cd cp_src/

    echo "Checking out stable branch 8.0 on Source Branch"
    git checkout 8.0

    echo "Checking out to new branch 8.0-git-history-$module-hbto"
    git checkout -b 8.0-git-history-$module-hbto

    echo "Rewriting cp_src branch for $module module"
    git filter-branch --subdirectory-filter $module -- --all
    mkdir $module
    git mv -k * $module
    git commit -am "[GIT] $module Git history"


    echo "Moving inside xDev Folder"
    cd ~/xDev/git
    echo "Copying vauxoo/account"
    cp -r vx-account    cp_dst
    echo "Moving inside cp_dst to migrage $module"
    cd cp_dst/
    echo "Checking out to new branch 8.0-git-history-$module-hbto"
    git checkout -b 8.0-git-history-$module-hbto

    echo "Adding local cp_src repo"
    git remote add cp_src ../cp_src

    echo "Fetching local cp_src repo"
    git fetch cp_src

    echo "Merging history branch from cp_src repo"
    git merge cp_src/8.0-git-history-$module-hbto --commit

    echo "Pushing history for $module module to vauxoo-dev/account"
    git push vauxoo-dev 8.0-git-history-$module-hbto

    echo "Making a pull request to vauxoo/account"
    hub pull-request -b vauxoo:8.0 -h vauxoo-dev:8.0-git-history-$module-hbto -m "[REM] Landing $module module from vauxoo/addons-vauxoo"

    echo "Deleting Source & Destination Folders"
    cd ..
    rm -rf cp_src cp_dst

    echo "Copying addons-vauxoo to delete $module module"
    cp -r addons-vauxoo cp_src
    echo "Moving inside cp_src to delete $module module"
    cd cp_src/

    echo "Checking out stable branch 8.0 on Source Branch"
    git checkout 8.0

    echo "Checking out to new branch 8.0-git-history-$module-hbto"
    git checkout -b 8.0-git-history-$module-hbto

    echo "Removing $module module from addons-vauxoo"
    git rm -rf $module
    git commit -am "[REM] $module got moved to vauxoo/account project"

    echo "Pushing branch to vauxoo-dev development project"
    git push vauxoo-dev 8.0-git-history-$module-hbto

    echo "Making a pull request to vauxoo/account"
    hub pull-request -b vauxoo:8.0 -h vauxoo-dev:8.0-git-history-$module-hbto -m "[ADD] Moving $module module from vauxoo/addons-vauxoo"

    echo "Deleting Source Folder"
    cd ..
    rm -rf cp_src

done < "$1"
