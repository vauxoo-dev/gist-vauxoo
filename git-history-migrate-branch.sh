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

ROOT_DIR=~/xDev/git
DST=account
SRC=addons-vauxoo
DEV=hbto
VER=8.0


echo "Moving inside $ROOT_DIR Folder"
cd $ROOT_DIR

while IFS='' read -r MODULE || [[ -n "$MODULE" ]]; do
    echo "Module: $MODULE"

    echo "Moving inside $ROOT_DIR Folder"
    cd $ROOT_DIR

    echo "Duplicating $SRC Folder to tmp-$SRC Folder"
    cp -r $SRC/ tmp-$SRC

    echo "Moving inside tmp-$SRC to migrate $MODULE"
    cd tmp-$SRC

    echo "Checking out stable branch $VER on $SRC Branch"
    git checkout $VER
    git fetch vauxoo-dev

    echo "Checking out to new branch $VER-tmp-$MODULE-$DEV"
    git checkout -b $VER-tmp-$MODULE-$DEV

    echo "Rewriting $SRC branch for $MODULE module"
    git filter-branch --subdirectory-filter $MODULE -- --all
    mkdir $MODULE
    git mv -k * $MODULE
    git commit -am "[GIT] $MODULE Git history"


    echo "Moving inside $ROOT_DIR Folder"
    cd $ROOT_DIR

    echo "Moving inside $DST to migrate $MODULE"
    cd $DST/

    echo "Checking out stable branch $VER on $DST Branch"
    git checkout $VER
    git fetch vauxoo-dev

    echo "Checking out to new branch $VER-git-history-$MODULE-$DEV"
    git checkout -b $VER-git-history-$MODULE-$DEV

    echo "Adding local $SRC repo"
    git remote add $SRC ../tmp-$SRC

    echo "Fetching local $SRC repo"
    git fetch $SRC

    echo "Merging history branch from $SRC repo"
    git merge $SRC/$VER-tmp-$MODULE-$DEV --commit

    echo "Pushing history for $MODULE module to vauxoo-dev/$DST"
    git push -f vauxoo-dev $VER-git-history-$MODULE-$DEV
    git fetch vauxoo-dev

    echo "Making a pull request to vauxoo/$DST"
    hub pull-request -b vauxoo:$VER -h vauxoo-dev:$VER-git-history-$MODULE-$DEV -m "[ADD] Landing $MODULE module from vauxoo/$DST" -i https://github.com/Vauxoo/$DST/issues/3

    echo "Deleting module branch on $DST Project"
    git checkout $VER
    git fetch vauxoo-dev
    git branch -D $VER-git-history-$MODULE-$DEV

    echo "Moving inside $ROOT_DIR Folder"
    cd $ROOT_DIR

    echo "Moving inside $SRC to delete $MODULE module"
    rm -rf tmp-$SRC

    echo "Moving inside $SRC to migrate $MODULE"
    cd $SRC

    echo "Checking out stable branch $VER on $SRC Branch"
    git checkout $VER
    git fetch vauxoo-dev

    echo "Checking out to new branch $VER-git-history-$MODULE-$DEV"
    git checkout -b $VER-git-history-$MODULE-$DEV

    echo "Removing $MODULE module from $SRC"
    git rm -rf $MODULE
    git commit -am "[REM] $MODULE got moved to vauxoo/$DST project"

    echo "Pushing branch to vauxoo-dev development project"
    git push -f vauxoo-dev $VER-git-history-$MODULE-$DEV
    git fetch vauxoo-dev

    echo "Making a pull request to vauxoo/$SRC"
    hub pull-request -b vauxoo:$VER -h vauxoo-dev:$VER-git-history-$MODULE-$DEV -m "[ADD] Landing $MODULE module from vauxoo/$SRC" -i https://github.com/Vauxoo/$SRC/issues/932

    echo "Deleting module branch on Src Project"
    git checkout $VER
    git fetch vauxoo-dev
    git branch -D $VER-git-history-$MODULE-$DEV

    echo "Switching to Lodi Project"
    cd $ROOT_DIR/lodigroup
    git checkout $VER
    git pull
    git fetch vauxoo-dev

    echo "Checking out to new branch $VER-git-history-$MODULE-$DEV"
    git checkout -b $VER-git-history-$MODULE-$DEV

    echo "Adding Dependency on Lodigroup to Vauxoo/$DST dev branch"
    sed  "/$SRC/d" oca_dependencies.txt > oca_dependencies.bak
    mv oca_dependencies.bak oca_dependencies.txt
    echo "$SRC git@github.com:Vauxoo-dev/$SRC.git $VER-git-history-$MODULE-$DEV" >> oca_dependencies.txt
    echo "$DST git@github.com:Vauxoo-dev/$DST.git $VER-git-history-$MODULE-$DEV" >> oca_dependencies.txt
    git commit -am "[DUMMY] $MODULE got moved to vauxoo/$DST project"

    echo "Pushing branch to vauxoo-dev development project"
    git push -f vauxoo-dev $VER-git-history-$MODULE-$DEV
    git fetch vauxoo-dev

    echo "Making a pull request to vauxoo/lodigroup"
    hub pull-request -b vauxoo:$VER -h vauxoo-dev:$VER-git-history-$MODULE-$DEV -m "[DUMMY] Moving $MODULE module from vauxoo/$SRC" -i https://github.com/Vauxoo/$DST/issues/3

    echo "Deleting module branch on Lodigroup Project"
    git checkout $VER
    git fetch vauxoo-dev
    git branch -D $VER-git-history-$MODULE-$DEV

done < "$1"
echo 'END'
