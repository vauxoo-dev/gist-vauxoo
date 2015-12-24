# odoo-instance

This script will let you to check and update the current instance related
branches.

For more help run ``odoo-instance --help``.

## Install

Need to create a alias to access to the binary file. From zero you can apply
the next commands. If not, you can run the install script inside the
odoo-instance folder.

```bash
$ cd
$ git clone git@github.com:vauxoo-dev/gist-vauxoo
$ echo "alias odoo-instance='${HOME}/gist-vauxoo/odoo-instance/odoo-instance'" >> ${HOME}/.profile
$ source ${HOME}/.profile
```

Now to check that the installation is complete you only need to type
``odoo-instance --help`` and you will see something like this

```bash
usage: odoo-instance [-h]
                     {status,update,paths,merged,no-merged,clean,checkout} ...

Given a list of instance branches will check/modify

positional arguments:
  {status,update,paths,merged,no-merged,clean,checkout}
    status              Check the status of the repos.
    update              Update the repos.
    paths               View the local path for instance.
    merged              Check the merged branchs.
    no-merged           Show the development branchs.
    clean               Clean out all the branchs.
    checkout            Will checkout to change to master branches.

optional arguments:
  -h, --help            show this help message and exit

Odoo Community Tool. Source code at git@github.com:vauxoo-dev/gist-vauxoo
Development/Coded by Katherine Zaoral <kathy@vauxoo.com> (github @zaoral)
```

## Usage

This is the way to using this script

```bash
$ odoo-instance <action> <instance_name>
```

## TODO

- convert this script to a python package.
- generate the json configuration file from the oca_dependencies file.
- manage a configuration file in the home folder to extract the repository
  data.
- add a version argument to the script.
