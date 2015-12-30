# odoo-i18n-export

This script will let you to generate the translation file for a given
module/modules given vu a command line interface. This script is a webservice
that connect to a odoo database and run the exportation wizards

You can generate the template translation file (pot) or the spanish translation
file (es.po)

Now you can make the exportation right away in the command line and do not
need to log into a Odoo instance. This is a hepfull script when runing remote
connections via consola.

## Install

Need to create a alias to access to python script. You can run the next
commands, or, you can run the install script inside the odoo-i18n-export
folder.

```bash
$ cd
$ git clone git@github.com:vauxoo-dev/gist-vauxoo
$ echo "alias odoo-i18n-export='${HOME}/gist-vauxoo/odoo-i18n-export/odoo-i18n-export'" >> ${HOME}/.profile
$ source ${HOME}/.profile
```
## Usage

To use this script just need to run

```bash
# Export pot files
$ odoo-i18n-export <module_path or modules_path>
# Export es.po files
$ odoo-i18n-export <module_path or modules_path> -f es_ES
# Export pot and es.po files
$ odoo-i18n-export <module_path or modules_path> -f all
```

## TODO

- convert this script to a python package.
- add a version argument to the script.
- activate the commit option when generating the translations files.
- manage the package version of the python package as said [here](http://stackoverflow.com/questions/458550/standard-way-to-embed-version-into-python-package)
- also generate an especific languange files, not only es_ES and pot files.
- activate option to create the database from 0 and then extract the files.
