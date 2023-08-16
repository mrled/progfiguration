.. _progfigsite:

``progfigsite`` packages
========================

``progfigsite`` packages are site-specific Python modules.
They must contain certain members (subpackages, modules, functions, and variables).


.. note::
    Member names not listed here are reserved for future use.
    If you add another member to your progfigsite package,
    it will work,
    but it may conflict with future progfiguration features.

    The best place to add site-specific code is in the :doc:`sitelib`.


.. toctree::
    :maxdepth: 2
    :caption: Contents:

    rootmembers.rst
    inventory.rst
    nodes.rst
    groups.rst
    roles.rst
    sitelib.rst
    builddata.rst

    development.rst
    defining-dependencies.rst
