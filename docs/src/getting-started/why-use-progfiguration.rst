.. _whyuse:

Why use progfiguration?
=======================

There's a lot of configuration management software out there.
Why use progfiguration?

* It's imperative, rather than declarative.
  Maybe you know that your configuration is complext from the start.
  Maybe you have wished you could write Python code directly in an Ansible task.

* It is designed to be run on the hosts themselves, rather than from a central server.
  This means that you can use it to configure hosts that are not always connected to the same trusted network,
  and that you don't need to worry about availability of a central server.

* It's fast to run.
  There's no heavy framework sitting between you and the host.
  It ships with a very small set of convenience functions
  for doing things like writing files and setting permissions.
  Caveat: this is not yet tested on large inventories, where it may need optimization.

* It's fast to deploy.
  ``progfigsite deploy``
  will package up the site, copy it to the hosts you specify, and run it.
  It's faster thn building a Pip package or running an Ansible role.

* It is deployable as a single file.
  Once you've written your configuration, build it with ``progfiguration build pyz``,
  and it will be packaged as a single executable file.
  You can even vendor your dependencies into the executable if you like.

  You can use this single file to deploy third party packages to the hosts you're configuring, too.

  Dependencies that must already be present are Python and
  (for any node that has secrets encrypted in the inventory) ``age``.
  TODO: allow installing ``age`` from the executable.

* It's designed to maximize user flexibility.
  Instead of or in addition to using generate single-file executables,
  you can build Pip packages or OS packages like RPMs and deploy that way.
  Roles offer the full power of Python.
  You can eschew built-in conveniences and conventions and write your own.

* It's designed to be *editable software*.
  If you need to modify it, you are encouraged to do so.


Why not use progfiguration?
---------------------------

It's worth calling out the limitations as well.

* Idempotency doesn't come for free.
  Among the benefits of declarative configuration is implied idempotency.
  Progfiguration lets you write non-idempotent code.

* It's much less featureful than alternatives.
  If you need to e.g. deploy CloudFormation stacks in Ansible, you can do so easily with an existing module.
  If you need to do this in progfiguration, you'll have to install boto3 and write the code yourself.

* It doesn't have the benefits of a large community or a rich sponsor.
  There isn't a large pool of talent in the job market already familiar with it.
