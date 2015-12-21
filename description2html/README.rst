================
description2html
================

This script will generate a ``index.html`` file from a ``README.rst`` file.

.. note:: This only works for odoo modules.

Install
=======

From local source::

    $ git clone https://github.com/vauxoo-dev/gist-vauxoo.git
    $ cd description2html
    # pip install .

.. TODO: From remote source::
    $ pip install --upgrade git@github.com:vauxoo-dev/gist-vauxoo/description2html
   .. TODO: need fix the project URL

Usage
=====

To generate/update ``index.html`` file from a ``README.rst`` file you just
need to go to your module path and run::

    description2hmtl -p .

The ``.`` is the ``<path>`` argument and can be:

- a module path: will update the description index.html of the given module.
- a multiple modules path: will update the index.html description of all the
  modules inside the path.

.. note:: For this script to work:

    1. The module need to have a ``README.rst`` file in the main directory.
    2. The module need to have this folder ``static/description/``.

Running this command will show you first a confirmation message that should
respond as y or n (yes/no). You can disable this confirmation by passing the
argument ``--no-confirm``.

An extra argument can be use, ``--pretty-style``. This argument will print a
index.html page using containers/container dark styles as the descriptions of
the odoo base modules. For example `account` module.

Report an issue `here <https://github.com/vauxoo-dev/gist-vauxoo/issues/new?body=package:%20
description2tml%0Aversion:%20
1.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_

For more help you can run ``description2html --help``.
