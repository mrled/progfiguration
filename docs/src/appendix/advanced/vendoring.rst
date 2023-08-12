Vendoring site dependencies
===========================

``progfiguration`` is designed to support vendoring.

When building pip or pyz packages with ``progfiguration build``,
it automatically vendors ``progfiguration`` core into
``progfigsite.autovendor.progfiguration``.

It is recommended that site-specific vendored dependencies be placed somewhere under
:doc:`/user-reference/progfigsite/sitelib` and imported from there.

When to vendor?
---------------

Vendoring is considered useful because it keeps packages self-contained.
Especially if there is unlikely to be a security concern,
sites should feel free to vendor dependencies.

Note that there is no need to vendor dependencies that can be installed in roles.
If you have a role that depends on some package, perhaps the imminently useful ``requests``,
you can simply install the package before importing it in the role.

Vendoring should only be necessary for packages that you need for the site to work at all.
For instance, if you are using a custom inventory that relies on YAML,
you might vendor ``PyYAML`` into your site.

Vendoring ``progfiguration`` core
---------------------------------

You can even vendor ``progfiguration`` core itself this way,
if you want to make changes to core components and don't mind maintaining a fork.

Consider filing a bug against progfiguration if there is a missing extension point
that would have allowed you to do what you needed in your own site.

In the future, we'd like to offer an easy command for showing differences between a vendored progfiguration and upstream.

When vendoring progfiguration core so that you can make changes to it, keep these ideas in mind:

- Be judicious. Add or change just one thing at a time, so that it's easy to understand what's different.
- Provide lots of documentation in comments. You'll have to port this code to each new version of progfiguration yourself.
