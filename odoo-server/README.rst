Odoo toolkit
------------

Make it easy create a new stance and run it, using unit test or without
test. The main feature is create a main base database and re used to do not
need to install everything every time. This make the times in development more
easy to handle

Manual
------

- `createdb_main`: create a new database named instance_base that is created
  with unit test active.
- `createdb_depends`: create a new database duplicating the instance_base to
  save time. This database will install the module given in command line
  argument and will receive the name module_base.
- `createdb_test`: create a new database module duplicate from module_base
  that will install the module given in the command line.
- `test`: run unit test for a given module.
- `run`: will only star odoo server for a given module (database has the same
  name of the module).
- `remote_docker`: after run t2d the resulting path can be pass to this
  script to generate the docker image and run a containter with it in the
  remote repo raditz.
- `odoo_server`: the main app that run odoo server. This not need to be used
  because the order commands use it preconfigured. Can also be use manually
  if needed.

TODO
----

- add a `install` command
- add a `test-only` command (stop after init).
- add a `update` command. 
- add `with-unit-test` and `with-log` parameters.
- add pkill command to make that the odoo instance stop. something like:
- this script need to be modify to work with t2d image.
- review the reinstallmodule script and merge it with odoo-server.

```
pkill "(openerp|odoo)" -fe -9
```
