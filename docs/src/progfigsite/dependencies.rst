Defining ``progfigsite`` dependencies
=====================================

Progfiguration core has no runtime dependencies,
and packages of it are always self-contained.

Progfigsite packages reference progfiguration core modules.
When building progfigsite packages with ``progfiguration build`` (see :doc:`/commands/progfiguration`),
progfigsite packages include progfiguration core in the :doc:`autovendor` so they are self-contained.

You can also build progfigsite packages without a vendored progfiguration core
by using standard Python build tools and a ``pyproject.toml``.

Progfigsite packages may use third party dependencies in one of two ways:

1.  For core functionality like in the :doc:`sitelib`.

    The simplest thing to do is to list the dependencies in ``pyproject.toml`` under ``project.dependencies``.
    This will cause the dependencies to be installed when building the package or installing it with a package manager.
    However, it will mean that ``progfiguration build pyz``, ``progfiguration run``,
    and ``progfiguration deploy`` will not work,
    as those commands assume a self-contained package.

    If your environment ensures that the dependencies are available at runtime,
    don't list them as ``project.dependencies`` in ``pyproject.toml``
    (though you may wish to list them somewhere under ``project.optional-dependencies``
    so you can easily install them during development).

    If not, you may wish to vendor them yourself.
    Don't use :doc:`autovendor` for this,
    but instead place them somewhere under :doc:`sitelib`.

2.  For dependencies that can be installed by a ``progfigsite`` role.

    For this use,
    you can list the dependencies in ``pyproject.toml`` under ``project.optional-dependencies``,
    and install them during development.
    Make sure your role installs them before using them,
    and then they will be available.

.. note::

    Progfiguration and progfigsite both have build-time dependencies when building pip packages.
    Building zipapp packages can be done entirely without dependencies.


The design is intended to give maximum flexibility to progfigisite users.
