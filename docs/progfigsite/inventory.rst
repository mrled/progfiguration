``progfigsite`` ``inventory.conf`` File
=======================================

An ``inventory.conf`` file must be present in the root of the ``progfigsite`` package.
The file should be in :mod:`configparser` format.

Here's an example from :mod:`example_site`:

.. literalinclude:: ../../tests/data/simple/example_site/inventory.conf
   :language: ini

Functions
---------

Unlike groups and nodes, functions don't have an object associated with them.
Functions play a similar role to :doc:`playbooks in Ansible </for-ansible-users/functions>`.
A function is mapped to a list of nodes and a list of roles.
When a node is provisioned, the roles associated with the function are applied to the node.
