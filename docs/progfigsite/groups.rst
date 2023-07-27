``progfigsite.groups`` Module
=============================

This module should contain a separate Python file for each group.
For instance:

.. code-block:: text

    progfigsite/
        __init__.py
        ...
        groups/
            __init__.py
            group1.py
            group2.py
            group3.py
            universal.py

Note that all nodes are members of the ``universal`` group.

Group files
-----------

Each group file should contain a class named ``group`` that is an instance of
:class:`progfiguration.progfigtypes.Bunch`.
Groups are only used for variable definitions,
so the only thing inside each group is a mapping of group names to variable values.

For instance, the node defined in :mod:`example_site.groups.group1`:

.. literalinclude:: ../../tests/data/simple/example_site/groups/group1.py
   :language: python

Group secret files
-----------------

If a group has secrets encrypted with ``progfiguration encrypt``,
they will be stored in a file named ``<group name>.secrets.json``
in the ``groups`` package.
