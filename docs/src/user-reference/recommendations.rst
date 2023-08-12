Recommendations
===============

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
