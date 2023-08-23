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

Each group file should contain a dict named ``group``.
Groups are only used for variable definitions,
so the only thing inside each group is a mapping of group names to variable values.

For instance, the node defined in :mod:`example_site.groups.group1`:

.. literalinclude:: ../../../..//tests/data/simple/example_site/groups/group1.py
    :language: python

Group secret files with AgeSecretStore
--------------------------------------

.. note:: Information in this section only applies to AgeSecretStore

    This section only applies to sites that use the
    :class:`progfiguration.sitehelpers.agesecrets.AgeSecretStore`
    secret storage implementation.
    It's what ships with progfiguration core so it's the easiest to get started with,
    but other secret storage backends will work differently.

If a group has secrets encrypted with ``progfiguration encrypt``,
they will be stored in a file named ``<group name>.secrets.json``
in the ``groups`` package.

Group secrets are encrypted with the public key of each member node.

When you add a node to a group with existing secrets,
you must re-encrypt the secrets file so that it can be decrypted by the new node.
You can do this with ``progfigsite decrypt ... | progfigsite encrypt ...``.
TODO: Add a single command to re-encrypt a group's secrets.

The ``universal`` group
-----------------------

The ``universal`` group is a special group that all nodes are members of.
It is used to define variables and secrets that are common to all nodes.
