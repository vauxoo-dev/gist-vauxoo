# pot-generator

This script will let you to generate the pot file for a given module via
command line interface, Now you do not need to log into a Odoo instance and
run the export wizard.

## Install

Need to create a alias to access to the binary file. From zero you can apply
the next commands. If not, you can run the install script inside the
`pot_generator` folder.

```bash
$ cd
$ git clone git@github.com:vauxoo-dev/gist-vauxoo
$ echo "alias pot-generator='${HOME}/gist-vauxoo/pot_generator/pot_generator.py'" >> ${HOME}/.profile
$ source ${HOME}/.profile
```
## Usage

To use this script just need to run

```bash
$ pot-generator <module_path or modules_path>

```

## TODO

- convert this script to a python package.
- add a version argument to the script.
- activate the commit option when generating the pot files.
- manage the package version of the python package as said [here](http://stackoverflow.com/questions/458550/standard-way-to-embed-version-into-python-package)
- also generate an especific languange files, not only pot files.
- activate option to create the database from 0 and then extract the files.
