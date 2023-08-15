Build and deploy
================

Once you have the first version of your site configured,
you need to deploy it.

Building packages
-----------------

You can build a Pip package with
``progfiguration build --progfigsite-python-path progfigsite pip``,
run from your virtual environment.
You can copy the result to the node(s) you created,
install it with ``pip``,
and run ``progfigsite apply NODENAME``,
and your node will apply its configuration!

You can also build a zipapp package with
``progfiguration build --progfigsite-python-path progfigsite pyz progfigsite.pyz``.
This can be run directly, the same way a Python script can be run,
and it includes both your ``progfigsite`` module
and the core ``progfiguration`` module in one file!
You can copy it to your remote node(s) and run it with ``python3 progfigsite.pyz``.

However, this is a bit cumbersome.
Building Pip packages is a little slow,
and it requires manual steps to copy and apply the configuration.

Building and deploying in one step
----------------------------------

Rather than calling core progfiguration with ``progfiguration build``,
you can call your own site's deploy method with ``progfigsite deploy``.
This will create a zipapp, copy it to the remote system(s),
and run it,
all in one step!

This does require SSH host keys to be set correctly in
``~/.ssh/known_hosts`` on your controller.
(In the future, we want to read ssh host keys from node objects,
but this hasn't been written yet.)

``progfigsite deploy --nodes node1 --apply``.

Custom build code
-----------------

Progfiguration is designed to support custom packages,
like RPMs or APKs.
See an example in the
`psyops progfigsite <https://github.com/mrled/psyops/blob/master/progfiguration_blacksite/progfiguration_blacksite/cli/progfigsite_buildapk_cmd.py>`_.

Next steps
----------

That's it!
You've created and deployed a simple progfigsite.

* Add the rest of your hosts, groups, roles, and functions to the inventory.
* Read :doc:`/user-reference/index` for a more complete exploration of the progfigsite API.
* Read :doc:`/design/index` to learn about the goals design decisions of the project.
* Add a link to your progfigsite package source to :doc:`/appendix/users`, if you wish.

If you like this software, please deploy something weird with it.
