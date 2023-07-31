progfigsite command
===================

Once you have created a progfiguration site (see :ref:`progfiguration-getting-started`),
you can use the configured ``progfigsite`` command to interact with it.

In order to use this command, you need to add a shim file to your site's Python package,
typically in ``<package>/cli/progfigsite_shim.py``,
which calls into :mod:`progfiguration.cli.progfiguration_site_cmd`.
See an example at :mod:`example_site.cli.progfigsite_shim`.
If you create your site from the example site as in :doc:`/getting-started/new-site`,
this file will be created for you.

Note that your progfigsite's ``pyproject.toml`` can call the command anything it wants.
(And of course the module name of the progfigsite is arbitrary, too.)
The default name is ``progfigsite``,
but you may wish to rename it to something that fits your site's name better.
See the ``[project.scripts]`` table in ``pyproject.toml`` to change this.

.. code-block:: console

    [project.scripts]
    progfigsite = "progfigsite.cli.progfigsite_shim:main"


Command-line help
-----------------

.. argparse::
    :module: progfiguration.cli.progfiguration_site_cmd
    :func: _make_parser
    :prog: progfigsite
