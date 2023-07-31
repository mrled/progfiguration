Why vendor progfiguration core?
===============================

When we build pip or zipapp packages with ``progfiguration build``,
progfiguration core is vendored into the package as ``progfigsite.autovendor.progfiguration``.

Why not just use a separate package for core and site?
While this is exactly the shape of problem that packaging systems (like pip) were invented for,
keeping progfiguration in a generic pip package means
the site package would have to depend on the core package,
which means that applying state requires managing two pacakges.

Also, the very fast zipapp packages don't understand dependencies.
