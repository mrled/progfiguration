Creating a New Progfiguration Site
==================================

See also :doc:`/user-reference/progfigsite/index`.

1.  Install ``progfiguration`` core.

        .. code-block:: bash

            python3 -m venv venv
            . venv/bin/activate
            pip install -U pip
            pip install progfiguration

2.  Create a new site from scratch.
    The name of your package is arbitrary, you can use anything you like.

        .. code-block:: bash

            progfiguration newsite \
                --path ./progfigsite \
                --name progfigsite \
                --description "This is a new progfigsite" \
                --controller-age-key-path ./progfigsite.controller.age

    This creates a new directory ``progfigsite`` (based on the ``--path`` you provided),
    and the ``age`` key for the :ref:`progfigsite-concept-controller`.

    Here's a table of the contents of the ``./progfigsite`` directory:

    +-----------------------------------------------+-----------------------------------------------+
    | File                                          | Description                                   |
    +===============================================+===============================================+
    | ``pyproject.toml``                            | A Python project file.                        |
    +-----------------------------------------------+-----------------------------------------------+
    | ``src/``                                      | The src directory for src-layout.             |
    +-----------------------------------------------+-----------------------------------------------+
    | ``src/progfigsite/``                          | The root of the actual Python package.        |
    |                                               | (The same name as the parent, e.g.            |
    |                                               | ``progfigsite/progfigsite/``).                |
    +-----------------------------------------------+-----------------------------------------------+
    | ``src/progfigsite/__init__.py``               | The root package exports some required        |
    |                                               | attributes.                                   |
    +-----------------------------------------------+-----------------------------------------------+
    | ``src/progfigsite/inventory.conf``            | An inventory config file for the site.        |
    +-----------------------------------------------+-----------------------------------------------+
    | ``src/progfigsite/inventory.py``              | The site's inventory module.                  |
    +-----------------------------------------------+-----------------------------------------------+
    | ``src/progfigsite/cli/``                      | A Python package for command line scripts.    |
    +-----------------------------------------------+-----------------------------------------------+
    | ``src/progfigsite/cli/progfigsite_shim.py``   | The file that is installed as the             |
    |                                               | ``progfigsite`` script.                       |
    +-----------------------------------------------+-----------------------------------------------+
    | ``src/progfigsite/nodes/``                    | A directory for node definitions.             |
    +-----------------------------------------------+-----------------------------------------------+
    | ``src/progfigsite/nodes/node1.py``            | An example node.                              |
    +-----------------------------------------------+-----------------------------------------------+
    | ``src/progfigsite/groups/``                   | A directory for group definitions.            |
    +-----------------------------------------------+-----------------------------------------------+
    | ``src/progfigsite/groups/universal.py``       | The universal group file.                     |
    +-----------------------------------------------+-----------------------------------------------+
    | ``src/progfigsite/groups/group1.py``          | An example group.                             |
    +-----------------------------------------------+-----------------------------------------------+
    | ``src/progfigsite/roles/``                    | A directory for role definitions.             |
    +-----------------------------------------------+-----------------------------------------------+
    | ``src/progfigsite/roles/role1.py``            | An example role.                              |
    +-----------------------------------------------+-----------------------------------------------+
    | ``src/progfigsite/sitelib/``                  | Site-specific utility functions etc.          |
    +-----------------------------------------------+-----------------------------------------------+
    | ``src/progfigsite/builddata/``                | Used to inject data at build time like        |
    |                                               | statically included packages, build date, etc.|
    +-----------------------------------------------+-----------------------------------------------+

    Not included in the table are a readme file and some empty ``__init__.py`` files
    which make directories into Python packages.

    NOTE: When changing this table, make corresponding updates to
    :class:`progfiguration.progfigsite_validator.ValidationResult` and
    :mod:`progfiguration.newsite`.

3.  Store your controller's age key securely.

    As noted above, we saved the controller's age key to the current directory.
    You should store it somewhere both secure and backed up.
    This might be somewhere in your home directory,
    in a secret store like ``gopass``,
    or wherever makes sense for your controller and your threat model.

    If you move it, make sure that the ``secrets.controller_age_path``
    configuration key contains the new location.

4.  Install your progfigsite package to the venv.

    Run ``pip install -e progfigsite``.
    This is required to get the ``progfigsite`` command added to your ``$PATH``,
    which we'll be using in later steps of this guide.
