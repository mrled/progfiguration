``progfigsite`` Development Environment
=======================================

Progfiguration core can be installed on its own and used to bootstrap a progfigsite.
You can install it standalone with one of:

*   pip from pypi:
    ``pip install progfiguration``
*   pip from a local checkout of the repository:
    ``git checkout https://github.com/mrled/progfiguration; cd progfiguration; pip install -e .``

In both of the above methods,
progfiguration finds progfigsite via ``progfigsite`` in Python path,
or via ``--progfigsite-package-path`` command-line argument

Progfigsites can be installed for local development with:

*   pip from a local checkout:
    ``git checkout https://example.com/progfigsite.git; cd progfigsite; pip install -e .``

    * progfigsite ``pyproject.toml`` AND progfiguration ``pyproject.toml``,
    * core ``progfiguration`` command installed from ``progfiguration`` package
    * ``progfigsite`` shim installed from ``progfigsite`` package
    * progfigsite finds ``progfiguration`` package in Python path, installed directly by pip
    * progfiguration finds ``progfigsite`` package in Python path, installed directly by pip

You can install and run a combined progfiguration core + progfigsite package with one of:

*   zipapp deployment from a package built with ``progfiguration build pyz``,
    which just requires copying the ``progfiguration.pyz`` file and running it

    * progfiguration ``pyproject.toml`` only
    * Runnable directly, invoking the ``progfiguration_site_cmd:main`` function
    * does not install core ``progfiguration`` command
    * progfigsite finds ``progfiguration`` package in Python path which includes root of zipapp
    * progfiguration finds ``progfigsite`` package in Python path which includes root of zipapp

*   a pip package built with ``progfiguration build pip``:
    ``pip install /path/to/progfigsite-x.y.z.tar.gz``

    * progfigsite ``pyproject.toml`` only
    * installs commands from progfigsite ``pyproject.toml``, which should include a shim for the ``progfiguration_site_cmd:main`` function
    * does not install core ``progfiguration`` command
    * progfigsite finds ``progfiguration`` package in ``autovendor`` directory because of ``ensure_autovendor()``
    * progfiguration finds ``progfigsite`` package in Python path because progfigsite was installed by pip


Building pacakges
-----------------

Progfigsite packages can be in *whatever format you want*.
If your hosts are RHEL, you might build RPMs.
The original hosts that progfiguration was written for were Alpine Linux, and consumed APKs.
Your own site might use something else,
and it can define instructions for building packages in whatever format you need.

Progfiguration core does support building two package types itself:
pip packages, and zipapp packages.

Building ``pip`` packages
-------------------------

TODO: pip packages not actually supported yet

Pip itself needs no introduction.
We keep the ability to build pip packages in progfiguration core,
rather than delegating it to progfigsite implementations,
for two reasons:

1.  It's universal.
    Any Python that can run progfiguration at all can install a progfigsite package via pip,
    including into a venv.
2.  It's the easiest way to build distribution-specific packages.
    RPMs can be built from Python build instructions,
    and so can APKs.

Building ``zipapp`` packages
----------------------------

:mod:`zipapp` is a little-known feature of the Python standard library.
In short, you can zip up any Python module and add a small ``__main__.py``
and execute it with the default Python interpreter just as if it were a simple Python text script.
This method allows embedding dependencies as well.
All code executed this way must be pure Python code (no C extensions).
We use zipapp because:

1.  Building a zipapp package is *extremely* fast
2.  It's deployable instantly to anywhere with a Python interpreter

You can build progfigsite packages with these two methods via ``progfiguration build pyz``,
and see the code in :mod:`progfiguration.progfigbuild`.

Building other package types
----------------------------

TODO: Include examples of building other package types like RPMs

TODO: Link to psyops progfigsite with APK example
