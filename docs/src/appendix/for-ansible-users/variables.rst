Variables: Ansible vs progfiguration
====================================

In ``progfiguration``, variables are passed explicitly to roles.
There is no such thing as a global variable,
and the number of places variables can be defined is much smaller than in Ansible.

This is also true of :doc:`templates </appendix/for-ansible-users/templates>` used by ``progfiguration``.

This is a deliberate design choice,
born out of frustration trying to debug Ansible playbooks
where variables are defined in many different places,
and it is not always clear which variable is being used.

In Ansible, large projects often end up prefixing variables with the role name
to avoid conflicts between variables with the same name in different roles.
This is a pretty good solution,
but it can lead to very long variable names,
and there is no way to enforce it.
One of Ansible's strengths is that it is easy for team members of all skill levels
to contribute changes to the configuration,
but this can be a problem when it comes to variable names.

You can get something like global variables with :doc:`/user-reference/progfigsite/sitelib`,
which is a site-specific place for utility functions and other code you wish to reuse.
It is recommended to create a ``constants.py`` or similar module
to define values that are used in many places.
