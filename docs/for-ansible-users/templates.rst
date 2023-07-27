Templates: Ansible vs progfiguration
====================================

Ansible templates are based on ``jinja2``.
They provide a lot of power out of the box.

Progfiguration does not ship with such a powerful template engine,
just `string.Template` from the Python standard library.
(We do provide `progfiguration.temple.Temple`
which uses ``{$}`` for variable substitution rather than the default ``$``,
which is a nicer fit for shell scripts.
Using it is completely optional.)

`string.Template` templates used by progfiguration:

* Require no third-party dependencies.
* Cannot contain logic like ``if`` or ``for`` statements, or include other templates.
* Require all variables to be passed in explicitly.
  It is always clear what variables are used by a template, and what their source is.
  (This is an intentional design decision; see :doc:`/for-ansible-users/variables`.)

jinja2 templates used by Ansible:

* Require a third-party dependency.
* Can contain logic like ``if`` or ``for`` statements, and include other templates.
* Can access variables from the environment, or from a file, or from a dictionary.
  It is easier to set variables, but also easier to accidentally use the wrong value.

Templates were one of the reasons I wanted to write progfiguration.
When working with large Ansible repositories,
I found it difficult to understand what variables were used by a template,
and where they came from.
