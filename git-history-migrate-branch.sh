#!/bin/bash
#/Usage: git-history-migrate-branch.sh module-list.txt instance-list.txt
# module-list.txt is a list of odoo modules to be migrated from a project to
# another. Must be one line per module.
# instance-list.txt is a list of odoo projects which are affected by the
# migration of this modules. Must be one line per instance.
# token.txt must be located on $HOME_DIR
# To create TOKEN you must go to github.com / Settings / Personal Access Token
# and create a new one. Beware: TOKEN is like a password so it be kept safe.
# Scripted by:
# Humberto Arocha <hbto@vauxoo.com>

HOME_DIR=/tmp
ROOT_DIR=$HOME_DIR/branches
DST=account
SRC=addons-vauxoo
DEV=hbto
VER=8.0
TOKEN=$(cat $HOME_DIR/token.txt)
AUTH="\"""Authorization: token $TOKEN""\""

echo "Moving inside $HOME_DIR Folder"
cd $HOME_DIR

if [ ! -d "$ROOT_DIR" ]; then
    echo "Creating Folder $ROOT_DIR"
    mkdir -p $ROOT_DIR
fi

echo "Moving inside $ROOT_DIR Folder"
cd $ROOT_DIR

for REPO in $SRC $DST
do
    echo "Checking if Folder $REPO already exists"
    if [ -d "$REPO" ]; then
        echo "Deleting Folder $REPO"
        rm -rf $REPO
    fi
    echo "Cloning $REPO Project"
    git clone git@github.com:Vauxoo/$REPO
    cd $REPO
    echo "Adding remote development branch to $REPO"
    git remote add vauxoo-dev git@github.com:Vauxoo-dev/$REPO
    echo "Switching back to $ROOT_DIR"
    cd $ROOT_DIR
done

while IFS='' read -r REPO || [[ -n "$REPO" ]]; do
    echo "Checking if Folder $REPO already exists"
    if [ -d "$REPO" ]; then
        echo "Deleting Folder $REPO"
        rm -rf $REPO
    fi
    echo "Cloning $REPO Project"
    git clone git@github.com:Vauxoo/$REPO
    cd $REPO
    echo "Adding remote development branch to $REPO"
    git remote add vauxoo-dev git@github.com:Vauxoo-dev/$REPO
    echo "Switching back to $ROOT_DIR"
    cd $ROOT_DIR
done < "$2"

while IFS='' read -r MODULE || [[ -n "$MODULE" ]]; do
    echo "Module: $MODULE"

    echo "Moving inside $ROOT_DIR Folder"
    cd $ROOT_DIR

    if [ -d "tmp-$SRC" ]; then
        echo "Deleting Folder tmp-$SRC"
        rm -rf tmp-$SRC
    fi

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
    title="[ADD] Landing $MODULE module from vauxoo/$DST"
    body="Related to https://github.com/Vauxoo/$DST/issues/3"
    head="vauxoo-dev:$VER-git-history-$MODULE-$DEV"
    base=$VER

    POST="{ \
                \"title\": \""$title"\", \
                \"body\": \""$body"\", \
                \"head\": \""$head"\", \
                \"base\": \""$base"\" \
            }"
    URL=https://api.github.com/repos/vauxoo/$DST/pulls
    PR="curl -H $AUTH -d '$POST' $URL"
    eval $PR

    echo "Deleting module branch on $DST Project"
    git checkout $VER
    git fetch vauxoo-dev
    git branch -D $VER-git-history-$MODULE-$DEV

    echo "Moving inside $ROOT_DIR Folder"
    cd $ROOT_DIR

    echo "Deleting  tmp-$SRC Because after being used is useless"
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
    title="[REM] Moving $MODULE module from vauxoo/$DST"
    body="Related to https://github.com/Vauxoo/$SRC/issues/932"
    head="vauxoo-dev:$VER-git-history-$MODULE-$DEV"
    base=$VER

    POST="{ \
                \"title\": \""$title"\", \
                \"body\": \""$body"\", \
                \"head\": \""$head"\", \
                \"base\": \""$base"\" \
            }"
    URL=https://api.github.com/repos/vauxoo/$SRC/pulls
    PR="curl -H $AUTH -d '$POST' $URL"
    eval $PR

    echo "Deleting module branch on $SRC Project"
    git checkout $VER
    git fetch vauxoo-dev
    git branch -D $VER-git-history-$MODULE-$DEV

    echo "Creating DUMMY Pull Request on Affected Projects"
    while IFS='' read -r INSTANCE || [[ -n "$INSTANCE" ]]; do
        echo "Instance: $INSTANCE"

        echo "Switching to $INSTANCE Project"
        cd $ROOT_DIR/$INSTANCE
        git checkout $VER
        git pull
        git fetch vauxoo-dev

        echo "Checking out to new branch $VER-git-history-$MODULE-$DEV"
        git checkout -b $VER-git-history-$MODULE-$DEV

        echo "Adding Dependency on $INSTANCE to Vauxoo/$DST dev branch"
        sed  "/$SRC/d" oca_dependencies.txt > oca_dependencies.bak
        mv oca_dependencies.bak oca_dependencies.txt
        echo "$SRC git@github.com:Vauxoo-dev/$SRC.git $VER-git-history-$MODULE-$DEV" >> oca_dependencies.txt
        echo "$DST git@github.com:Vauxoo-dev/$DST.git $VER-git-history-$MODULE-$DEV" >> oca_dependencies.txt
        git commit -am "[DUMMY] $MODULE got moved to vauxoo/$DST project"

        echo "Pushing branch to vauxoo-dev development project"
        git push -f vauxoo-dev $VER-git-history-$MODULE-$DEV
        git fetch vauxoo-dev

        echo "Making a pull request to vauxoo/$INSTANCE"
        title="[DUMMY] Moving $MODULE module from vauxoo/$SRC"
        body="Related to https://github.com/Vauxoo/$DST/issues/3"
        head="vauxoo-dev:$VER-git-history-$MODULE-$DEV"
        base=$VER

        POST="{ \
                    \"title\": \""$title"\", \
                    \"body\": \""$body"\", \
                    \"head\": \""$head"\", \
                    \"base\": \""$base"\" \
                }"
        URL=https://api.github.com/repos/vauxoo/$INSTANCE/pulls
        PR="curl -H $AUTH -d '$POST' $URL"
        eval $PR

        echo "Deleting module branch on $INSTANCE Project"
        git checkout $VER
        git fetch vauxoo-dev
        git branch -D $VER-git-history-$MODULE-$DEV

    done < "$2"

done < "$1"
echo 'END'
