`mkcontainer`
---

A bash script to rapidly set up your Odoo development containers.

## Motivation

When setting up an Odoo development container there are always a few tasks that one has to do. They can be divided in three categories:

 1. **Mandatory tasks that *cannot* be included in the image**
     1. Copying personal SSH keys in the container
     2. Installing the main module with `odoo-bin -i`
 2. **Optional tasks that *cannot* be included in the image**
    1. Adding personal configuration files for VSCode
    2. Executing some custom SQL queries to change the demo data
 3. **Optional tasks that *could* be included in the image**
    1. Having odoo `chown` all `/home/odoo`
    2. Making `odoo` sudoer
    3. Installing `pre-commit-vauxoo`


For example, adding personal configuration files to VSCode could be useful to automatically install extensions or set up the integrated debugger and linter. Making `odoo` sudoer allows you to log in the docker as odoo and do everything without ever changing user. Custom SQL queries could be useful to add Mitchell Admin to various groups or to add a user with password and TOTP without doing the flow with the email. Installing Jupyter Lab can give a much nicer interface for `odoo-bin shell`!

With `mkcontainer` you can do all of these tasks either individually when the container is already running, or all at once at container creation.

## Configuration

At the top of the source file there is a section
```
####################
# Config           #
####################
```

You can edit all those variables to fit your case. If you want to see their documentation, comment out all of them and run `mkcontainer`. This will print the descriptions for each variable and exit.

## Usage

```
mkcontainer --help
```

Will show all the arguments. There are `Actions` and `Options`. An action is the operation that `mkcontainer` will perform and an option complements said operation.

You can specify only one action and all the options you want (although only a subset of them may be relevant for a given action).

You can tell an action from an option because actions start with a capital letter (except `-h / --help`).

After changing the configuration to fit your needs, it's as simple as calling
```
mkcontainer
```
The script is interactive so it's not fit for usage in other scripts.

### Examples
```
mkcontainer --Sql --name mycontainer
```
will perform the action `--Sql` which executes a custom `.sql` file in the database, the option ` --name` specifies the container where this action is performed.

Another example is
```
mkcontainer --Install mymodule test
```
will install the module `mymodule` in the database `test`. In this case, unlike the previous example, the action `--Install` comes with two arguments (one mandatory and one optional). The action will be executed on the default container (provided in the configs).

```
mkcontainer --image "quay.io/vauxoo/customer:tag" --name mycontainer
```
This is a call without an action. In this case `mkcontainer` will execute the default action, which basically performs all actions in sequence. You can personalize this default action by editing the function `run_all`
```
run_all () {

    ...
    # Add code here
}
```
This default action is typically run to create the container for the first time, whereas the other ones are always run on an already existing container.

For this reason `mycontainer` will be the name of the *newly created container* and if one with the same name exists, you will be asked to either eliminate it, or choose a different name.

Since `--image` is passed, instead of using the image provided in the configs, `mkcontainer` will use the passed repository and tag, pulling it from remote if not present in local.

**Warning**: If you create more than one container, use the `--port` option to define a new port,
otherwise docker run will fail. You have to provide only the http port and the other ones will
be defined automatically by applying the same shift from 8069.

## Ancillary files
This script comes with a few complementary files:

 - `launch.json`: It contains the configuration for VSCode debugger
 - `settings.json`: It contains some (opinionated) VSCode settings
 - `devcontainer.json`: It contains the configurations for the DevContainer
 - `kernel.json`: It contains the configuration for the Odoo Jupyter Kernel
 - `jupy_wrapper.py`: It's a script to launch an Odoo kernel in Jupyter (it works like `odoo-bin shell` but it's a notebook).
 - `setup.sql`: Example of an SQL script that can be run in the container

All these files will be copied inside the container via some actions of `mkcontainer`. You can edit them to fit your needs, or even add more: for example `mkcontainer` will recognize any `.sql` file in the current folder and make you choose which one you want to use.
