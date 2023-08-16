Vendoring site dependencies
===========================

``progfiguration`` is designed to support vendoring.

It is recommended that site-specific vendored dependencies be placed somewhere under
:doc:`/user-reference/progfigsite/sitelib` and imported from there.

Vendoring and static inclusion
------------------------------

These two concepts are distinct, but there is some overlap.

Vendoring
    Copying a dependency into your own source tree.

Static inclusion
    Copying a dependency into your assembled package.
    Analogous to static linking in languages like C and Go.

Both vendoring and static inclusion have security implications.
Using either strategy implies accepting the responsibility of handling these yourself,
and/or the risks of failing to do so.

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

When to statically include?
---------------------------

Static inclusion means your package build system handles dependency updates.
This isn't as easy to manage or as timely as handling dependency updates on remote systems for normal packages.
However, for the special needs of progfigsite packages,
this might be good enough.

Statically including ``progfiguration`` core
--------------------------------------------

When building pip or pyz packages with ``progfiguration build``,
it copies ``progfiguration`` core into
``progfigsite.builddata.staticinclude.progfiguration``.

Vendoring ``progfiguration`` core
---------------------------------

You can vendor ``progfiguration`` core if you prefer.
You might wish to do this to make changes to core components.
Doing so means you must maintain your fork yourself.

Consider filing a bug against progfiguration if there is a missing extension point
that would have allowed you to do what you needed in your own site.

When vendoring progfiguration core so that you can make changes to it, keep these ideas in mind:

- Be judicious. Add or change just one thing at a time, so that it's easy to understand what's different.
- Provide lots of documentation in comments. You'll have to port this code to each new version of progfiguration yourself.
