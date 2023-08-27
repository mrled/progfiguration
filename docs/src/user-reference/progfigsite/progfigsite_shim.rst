The ``progfigsite`` shim
========================

This shim is a thin wrapper around the :func:`progfiguration.cli.progfiguration_site_cmd.main`.
It makes sure that the static include directory is in the Python path,
and then calls the main function.

It's the entrypoint for the ``progfigsite`` command in ``pyproject.toml``.

It should be copied unchanged into your project
under ``<package_root>/cli/progfigsite_shim.py``.

.. literalinclude:: ../../../../tests/data/simple/example_site/cli/progfigsite_shim.py
    :language: python
