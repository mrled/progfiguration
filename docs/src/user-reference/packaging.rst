Packaging process
=================

After you have a site repository,
you can build a package with ``progfiguration build``.
This command copies the core package into the site repository,
sets some build-time data like a version and datestamp,
and builds a package for you.

With ``progfiguration build pyz``, you can build a **zipapp package**.
This is a zip file in a specific format which can be run directly like any Python script.
It has a version number in its filename,
but it is not a versioned package that can be installed, upgraded, or downgraded --
it's just a simple file.

Progfiguration core also can build pip packages with ``progfiguration build pip``.
These take longer to build,
but have real version numbers and can be installed anywhere a Pip package can.
Many operating system package systems support building Pip packages into OS packages,
like RPM and APK,
so you can use this as a base to build packages for your OS if that fits your use case --
see the context manager :class:`progfiguration.progfigbuild.ProgfigsitePythonPackagePreparer`
and `progfiguration-blacksite-buildapk <https://github.com/mrled/psyops/blob/master/progfiguration_blacksite/progfiguration_blacksite/cli/progfigsite_buildapk_cmd.py>`_
for an example that uses it.

Why statically include progfiguration core?
-------------------------------------------

When we build pip or zipapp packages with ``progfiguration build``,
progfiguration core is statically included into the package as
``progfigsite.autovendor.progfiguration``.

Why not just use a separate package for core and site?
While this is exactly the shape of problem that packaging systems (like pip) were invented for,
keeping progfiguration in a generic pip package means
the site package would have to depend on the core package,
which means that applying state requires managing two pacakges.

Also, the very fast zipapp packages cannot be used as dependencies.

Recommendations
---------------

* Use a versioning scheme for the progfigsite package that is based on the date.

  Unlike stable libraries and programs for end users,
  configuration packages change very frequently.

  You may want to modify-build-deploy without committing,
  especially in development,
  and ``progfigsite deploy ...`` will generate zipapps with the version number in the filename.

  You shouldn't tie your site's version to the version of progfiguration core,
  by for instance using ``1.core-version.site-version``,
  because this means that you can never deploy a version of your site that uses a new version of progfiguration core
  without committing to the new core version permanently.

* Add commands that will only be run from your controller as scripts in your progfigsite package.

  `progfiguration_blacksite <https://github.com/mrled/psyops/tree/master/progfiguration_blacksite>`_
  does this with a script that builds Alpine .apk packages,
  `progfiguration-blacksite-buildapk <https://github.com/mrled/psyops/blob/master/progfiguration_blacksite/progfiguration_blacksite/cli/progfigsite_buildapk_cmd.py>`_.
  Write the script inside the ``cli`` module
  and add it to ``[project.scripts]`` in ``pyproject.toml``.
