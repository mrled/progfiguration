``progfigsite.roles`` Module
============================

This module should contain a separate module for each role.
Simple roles may be single-file modules;
more complex roles or roles with included data files can be packages.
For instance:

.. code-block:: text

    progfigsite/
        __init__.py
        ...
        roles/
            __init__.py
            role1.py
            role2/
                __init__.py
                datafile.txt
                ...
            ...

Role packages
-------------

Each role module should contain a subclass of :class:`progfiguration.inventory.roles.ProgfigurationRole`
with the name ``Role``.

For instance, the node defined in :mod:`example_site.roles.settz`,
which set's a node's timezone:

.. literalinclude:: ../../tests/data/simple/example_site/roles/settz.py
   :language: python

Some things worth noting about roles:

*   They *must* be annotated with ``@dataclass(kw_only=True)``
*   Dataclass fields are arguments to the role,
    which may be defined on nodes and/or groups.
*   The ``apply`` function contains the logic for applying the role to a node.
    It can reference fields.
*   An optional ``result`` function can be defined to return a dict of values.
    **This result cannot rely on ``apply()`` having been called.**
    Yes, arguably this is a bad name.

TODO: show good and bad examples of ``.result()`` methods.
