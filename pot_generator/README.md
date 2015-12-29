# pot-generator

This script will let you to generate the pot file for a given module via
command line interface, Now you do not need to log into a Odoo instance and
run the export wizard.

## Install

Need to create a alias to access to the binary file. From zero you can apply
the next commands. If not, you can run the install script inside the
pot_generator folder.

```bash
$ cd
$ git clone git@github.com:vauxoo-dev/gist-vauxoo
$ echo "alias pot-generator='${HOME}/gist-vauxoo/pot_generator/pot_generator.py'" >> ${HOME}/.profile
$ source ${HOME}/.profile
```
## Usage

To use this script fist need to enter into the `pot_generator.py` file and
configure the next variables

```python
SERVER = 'localhost'
DB='ovl70'
PROTOCOL = 'xmlrpc'
PORT = 10000
TIMEOUT = 4000
USER = 'admin'
PASSWD = 'admin'
SRC_PATH = '/home/hbto/bzr_projects/_VE/70_ovl_branches/ovl70'
```

Then just need to run

```bash
$ pot-generator

```

## TODO

- use argparse to pass all the parameters via command line.
- convert this script to a python package.
- add option to generate pot file only for a given module.
- add a version argument to the script.
- replace bzr options to git options.
