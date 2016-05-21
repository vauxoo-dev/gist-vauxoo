#!/bin/bash
#/Usage: git-history-migrate-branch.sh module-list.txt instance-list.txt
# module-list.txt is a list of odoo modules to be migrated from a project to
# another. Must be one line per module.
# instance-list.txt is a list of odoo projects which are affected by the
# migration of this modules. Must be one line per instance.
# token.txt must be located on $HOME_DIR
# To create TOKEN you must go to github.com / Settings / Personal Access Token
# and create a new one. Beware: TOKEN is like a password so it be kept safe.

# This could be helpful for rewriting history on project
# https://developer.atlassian.com/blog/2015/08/grafting-earlier-history-with-git/

# Scripted by:
# Humberto Arocha <hbto@vauxoo.com>

HOME_DIR=/tmp
ROOT_DIR=$HOME_DIR/branches
USR_DST=vauxoo
USR_SRC=hbto
DST=account
SRC=addons-vauxoo
DEV=hbto
VER=8.0
TOKEN=$(cat $HOME_DIR/token.txt)
AUTH="\"""Authorization: token $TOKEN""\""
FILEDIR_LIST=""

echo "Moving inside $HOME_DIR Folder"
cd $HOME_DIR

if [ ! -d "$ROOT_DIR" ]; then
    echo "Creating Folder $ROOT_DIR"
    mkdir -p $ROOT_DIR
fi

echo "Moving inside $ROOT_DIR Folder"
cd $ROOT_DIR

echo "Checking if Folder $SRC already exists"
if [ -d "$SRC" ]; then
    echo "Deleting Folder $SRC"
    rm -rf $SRC
fi
echo "Cloning $SRC Project"
git clone git@github.com:$USR_SRC/$SRC

cd $SRC

echo "Adding remote development branch to $DST"
git remote add vauxoo-dev git@github.com:Vauxoo-dev/$DST

while IFS='' read -r MODULE || [[ -n "$MODULE" ]]; do
    echo "File/Directory to Delete: $MODULE"
    FILEDIR_LIST+=" $MODULE"
done < "$1"

echo "Cleaning the files"
echo "Cleaning the file will take a while, depending on how busy your repository has been."
FILTER_CMD="git filter-branch --tag-name-filter cat --index-filter ""'""git rm -r --cached --ignore-unmatch $FILEDIR_LIST""'"" --prune-empty -f -- --all"
eval $FILTER_CMD

echo "Reclaiming space"
rm -rf .git/refs/original/
git reflog expire --expire=now --all
git gc --prune=now
git gc --aggressive --prune=now

echo '*** END ***'
