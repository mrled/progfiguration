Entrypoints
===========

Some code from progfigsite packages must be able to run
even when progfiguration core is not installed.


Retrieving the version...
-------------------------

The version is calculated dynamically per ``pyproject.toml``,
so it must be available even when the module isn't installed.
The site must implement the function ``progfigsite.get_version``,
by e.g. defining ``get_version()`` in ``progfigsite/__init__.py``.

When ``setuptools`` looks in this module for the version,
it does *not* do a normal python import,
where first it loads ``progfigsite``, then the ``version`` submodule.
Instead, it reads the file in isolation.
The version file can only use code that is available in this unusual context.
This is why progfiguration core can't provide a default or helper function for sites --
the helper function would require progfiguration core to be installed,
but we can't guarantee that in all the of the scenarios where we use it go get the version.

... when building a package
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Building progfigsite pacakges must be done via ``progfiguration build``,
in order to inject build data like the version and build date,
and statically include progfiguration core.

(``progfiguration build`` does use the Python ``build`` module under the hood,
but just running ``python3 -m build ...`` by itself
will not result in a proper progfigsite package.)

Example
    ``progfiguration build ...``

Working?
    Yes

Progfigsite installed to Python path?
    No

Progfiguration core installed to Python path?
    Yes

... when installing a package
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

For pip packages, the version is baked in to the package metadata and ``get_version()`` is not used.
For zipapp packages, there is no inherenent concept of a "version" or "install time" --
it's just zip file with some data at the front to tell the operating system to use the Python interpreter to run it,
similar to a plain text Python script.
(Either type of package might call ``get_version()`` once it's loaded,
for instance if the user runs ``progfigsite version`` or similar;
this case is discussed below.)

Example
    ``pip install progfigsite``

Working?
    Yes

Progfigsite installed to Python path?
    No

Progfiguration core installed to Python path?
    No

... when installing from source with core
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A progfigsite's ``pyproject.toml`` does *not* list progfiguration core as a dependency,
because when the package is built, we will statically include it.
This means that when running ``pip install -e .``,
progfiguration core must have already been installed previously.

We don't expect that most users will use this method.
A site's users will install built packages or run zipapps directly,
and site developers will install the ``development`` extras (see below).

Example
    ``pip install progfiguration && pip install -e .``

Working?
    Yes

Progfigsite installed to Python path?
    No

Progfiguration core installed to Python path?
    Yes

... when installing from source without core
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The ``development`` extras for a progfigsite typically do list progfiguration core as a dependency,
along with build and development packages like ``setuptools``, ``black``, etc.
Site developers typically opt for this installation method on development machines.

Example
    ``pip install -e '.[development]'``

Working?
    Yes

Progfigsite installed to Python path?
    No

Progfiguration core installed to Python path?
    No

... at runtime
^^^^^^^^^^^^^^

The version code is also called sometimes at runtime,
for instance when running ``progfigsite version``.
However, this just uses normal Python imports,
so we don't need to do anything special to make sure it works.

Example
    ``progfigsite version``

Working?
    Yes

Progfigsite installed to Python path?
    Yes

Progfiguration core installed to Python path?
    Yes, perhaps via static includes

Running the progfigsite command line program...
-----------------------------------------------

The progfigsite command is installed as :doc:`/user-reference/progfigsite/progfigsite_shim`
as an entrypoint in ``pyproject.toml``.
In this scenario, the code is already present on the system,
however, the core module may be statically included in the package
and not available in the default Python path.

*   From a zipapp (e.g. ``/path/to/progfigsite.pyz``)
*   From an installed built package (e.g. a .tar.gz or .whl package installed with ``pip install progfigsite``)
*   From the source code installed as editable with ``pip install -e .``

... from a zipapp
^^^^^^^^^^^^^^^^^

When Python runs a zipapp package,
it places the path to the zipapp in the Python path,
making any zipped subdirectories available for direct importing via ``import progfigsite`` or similar.
Then it looks for a file called ``__main__.py`` in the root of the zip file and runs it.

See ours in :func:`progfiguration.progfigbuild.build_progfigsite_zipapp`.
We import the progfigsite package by name and call
:func:`progfiguration.cli.progfiguration_site_cmd:main`,
just like the shim does.
Unlike the shim, progfiguration core is already in the Python path
because it's also copied to the root of the zipfile,
so ``__main__.py`` ends up simpler than ``progfigsite_shim.py``.

Example
    ``/path/to/progfigsite.pyz``

Working?
    Yes

Progfigsite installed to Python path?
    Yes

Progfiguration core installed to Python path?
    Yes

... from an installed package
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

When a progfigsite package is built,
the progfiguration core package is copied inside ``builddata.static_include``.

The ``pyproject.toml`` specifies an entrypoint in ``progfigsite.cli.progfigsite_shim:main``,
which adds the ``static_include`` directory to the Python path
and then runs :func:`progfiguration.cli.progfiguration_site_cmd:main`.

That file looks something like this:

.. code:: python

    #!/usr/bin/python3
    # -*- coding: utf-8 -*-
    import re
    import sys
    from progfigsite.cli.progfigsite_shim import main
    if __name__ == "__main__":
        sys.argv[0] = re.sub(r"(-script\.pyw|\.exe)?$", "", sys.argv[0])
        sys.exit(main())

However, this is a a normal Python import,
which means that the line
``from progfigsite.cli.progfigsite_shim import main``
first loads the ``progfigsite`` module, then the ``cli`` module,
and then the ``progfigsite_shim`` module,
before running ``main()``.

This is different from setuptools calling ``get_version()``.
Setuptools does not do a normal Python import;
it just finds the file directly and tries to load it.

This means that for ``get_version()``,
it doesn't matter if the root ``progfigsite`` module tries to import progfiguration core
or does anything else that might fail.
But when tring to run an installed pacakge,
the root ``progfigsite`` module (and also ``cli`` and ``progfigsite_shim``)
must be importable without error even if progfiguration core is not already installed.
The shim places progfiguration core in the Python path,
so we can't import anything from progfiguration core until the shim runs.

Example
    ``pip install progfigsite && progfigsite ...``

Working?
    Yes

Progfigsite installed to Python path?
    Yes

Progfiguration core installed to Python path?
    Yes

... from the source code installed as editable
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

When installing this way, progfiguration core will already be in the Python path,
so this just behaves like a normal Python import.

Recall that running ``pip install -e .`` is unusual,
and in that case progfiguration core must already be in the Python path,
and that running ``pip install -e '.[development]'``
will install progfiguration core before installing the site.
Either way, the core package is available before the progfigsite program is run.

Example
    ``pip install -e '.[development]'``

Working?
    Yes

Progfigsite installed to Python path?
    Yes

Progfiguration core installed to Python path?
    Yes

Importing as a library...
-------------------------

*   From an installed built package (e.g. a .tar.gz or .whl package installed with ``pip install progfigsite``)
*   From the source code installed as editable with ``pip install -e .``
*   From progfiguration core by its filesystem path with ``importlib.import_module`` even if not installed to the Python path
*   From progfiguration core by its module name if it is installed to the Python path

... from an installed package
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This is unusual, and we may decide not to support it by default for progfigsite packages.

Example
    ``pip install ./my-progfigsite-package.tar.gz``, then ``import progfigsite``.

Working?
    Unknown

Progfigsite installed to Python path?
    Yes

Progfiguration core installed to Python path?
    No

    The core package may not be in the Python path,
    but it will be available under ``progfigsite.builddata.static_include``;
    importers may import that first.

... from the source code installed as editable
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Example
    ``pip install -e '.[development]'``, then ``import progfigsite``

Working?
    Yes

Progfigsite installed to Python path?
    Yes

Progfiguration core installed to Python path?
    Yes

... from progfiguration core by its filesystem path
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This will work as long as :func:`progfiguration.sitewrapper.set_progfigsite_by_module_name` has been called.
Progfiguration core uses :func:`progfiguration.sitewrapper.get_progfigsite` to reference it.

Example
    ``sitewrapper.get_progfigsite()`` from progfiguration core

Working?
    Yes

Progfigsite installed to Python path?
    Yes

Progfiguration core installed to Python path?
    Yes

Alternative entrypoints...
--------------------------

Sites may add alternative entrypoints as scripts in their ``pyproject.toml``.
These are not accessible from the zipapp,
but are available when installed via pip.

... from an installed package
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This is a rare case,
since progfigsite packages are expected to be used via zipapp at least some of the time.
However, it will work as long as the process used in the cli shim is followed:

..  literalinclude:: ../../../src/progfiguration/newsite/progfigsite_shim.py.temple
    :language: python

(Substitute ``{$}name`` with the name of your progfigsite package.)

Working?
    Yes

Progfigsite installed to Python path?
    Yes

Progfiguration core installed to Python path?
    No

    The core package may not be in the Python path,
    but it will be available under ``progfigsite.builddata.static_include``;
    importers may import that first.

... from source code installed as editable
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This might be useful for build scripts, such as
`progfiguration-blacksite-buildapk <https://github.com/mrled/psyops/blob/master/progfiguration_blacksite/progfiguration_blacksite/cli/progfigsite_buildapk_cmd.py>`_

Working?
    Yes

Progfigsite installed to Python path?
    Yes

Progfiguration core installed to Python path?
    No

    The core package may not be in the Python path,
    but it will be available under ``progfigsite.builddata.static_include``;
    importers may import that first.
