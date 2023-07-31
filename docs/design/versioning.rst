Versioning progfiguration and progfigsite packages
==================================================

Progfiguration is versioned directly, by setting a version in
pyproject.toml.

Progfigsite packages are versioned dynamically, by exporting a
``mint_version() -> str`` function in the package root.

``progfiguration build`` will run that function to mint a new version
number, and then record it into the package it builds.

When a package is built from ``progfiguration build``, the progfigsite
version is used as the package version; the version of progfiguration
core is not part of the package version at all. If it were, you would
not be able to download progfiguration core in a new version of the
progfigsite package.

Progfigiste packages also must implement ``get_version() -> str``,
which should try to retrieve a version from ``progfigsite.builddata.version``
if that module exists,
and otherwise fall back to some arbitrary very low fallback version number, like ``0.0.1a1``.
The build system will create the module ``progfigsite.builddata.version`` at build time,
and include a version (generated from ``mint_version()``) and a datestamp.

You can see an example of this in :mod:`example_site`.

Customizations
--------------

These functions are implemented in the site to allow for customization.
For instance, you might:

* Retrieve a build number from CI
* Automatically pull a git revision and whether it is dirty
