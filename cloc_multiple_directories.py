"""
# cloc_multiple_directories

    If you have the directory but you do not have the database, Cloc documentation does
    not provide a recursive way to get the number of line of code of every module inside
    a repository. This script solves that to get a table with each module inside a repository
    with just one line command and save that table in cloc_file.log

## Install

    ```bash
    $ cd
    $ git clone git@github.com:vauxoo-dev/gist-vauxoo
    ```
    Then use it as a normal python script.

## Usage

    This is the way to using this script (in the same directory as cloc_multiple_directories.py)
    ```bash
    $ python cloc_multiple_directories.py <odoo_bin_path> <repo_path>
    ```

## Tested

    This script was tested in python 3.7.
"""


import os
import sys
from subprocess import call


def handle_arguments():
    """Just to verify if there are two arguments"""
    if len(sys.argv) != 3:
        raise IndexError(
            "Please, remember only add odoo_bin path and repo_path. Example: "
            "python cloc_multiple_directories.py /home/odoo/odoo-15.0/odoo-bin "
            "/home/odoo/odoo-15.0/addons/"
        )
    odoo_bin_path = sys.argv[1]  # /home/odoo/odoo-15.0/odoo-bin
    repo_path = sys.argv[2]  # /home/odoo/odoo-15.0/addons/
    return odoo_bin_path, repo_path


def execute_odoo_cloc(odoo_bin_path, repo_path):
    """
    Search all subdirectories in the repo path except those which start with .
    as .git or .github directories and apply the command odoo cloc to resume the
    counting in a table and this method saves the result in a file called cloc_file.log

    Params:
        odoo_bin_path: str
            full odoo-bin path
        repo_path: str
            full repository path to count the lines of code
    """
    try:
        path_to_count = ""
        for directory in [
            d
            for d in os.listdir(repo_path)
            if os.path.isdir(os.path.join(repo_path, d)) and not d.startswith(".")
        ]:
            path_to_count = "%s-p %s " % (
                path_to_count,
                os.path.join(repo_path, directory),
            )
        call("%s cloc %s> ./cloc_file.log" % (odoo_bin_path, path_to_count), shell=True)
    except FileNotFoundError:
        raise FileNotFoundError(
            "Please, check if valid paths were included. Example: "
            "python cloc_multiple_directories.py /home/odoo/odoo-15.0/odoo-bin "
            "/home/odoo/odoo-15.0/addons/"
        )
    except NotADirectoryError:
        raise NotADirectoryError(
            "Please, check if odoo_bin_path is first and then the "
            "repo_path. Example: python cloc_multiple_directories.py "
            "/home/odoo/odoo-15.0/odoo-bin /home/odoo/odoo-15.0/addons/"
        )


def main():
    odoo_bin_path, repo_path = handle_arguments()
    execute_odoo_cloc(odoo_bin_path, repo_path)


if __name__ == "__main__":
    main()
