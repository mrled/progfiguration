dynvertest: test dynamic versioning in Python
=============================================

Does Python packaging tooling support calling a function to get the
version name at package build time? It depends on the tooling in
question. This is an experiment to answer that question for packages
built with ``setuptools`` and ``pyproject.toml``.

**At the time of this experiment, 2023-06-17, with setuptools 65.5.0
running on Python 3.11.4, a version can be set to a function.**

See this with:

.. code:: sh

   python3 -m venv venv
   . venv/bin/activate
   pip install -e .

It will show a specific version being installed, like:

.. code:: text

   (venv) user@host> pip install -e .
   Obtaining file:///Users/mrled/Documents/Repositories/pptt2
     Installing build dependencies ... done
     Checking if build backend supports build_editable ... done
     Getting requirements to build editable ... done
     Preparing editable metadata (pyproject.toml) ... done
   Building wheels for collected packages: dynvertest
     Building editable for dynvertest (pyproject.toml) ... done
     Created wheel for dynvertest: filename=dynvertest-0.0.1689623616-0.editable-py3-none-any.whl size=2748 sha256=9aa55b4a860a2fde124d628b4b50e0f2865b4ce4b0acbb083d884853363ae136
     Stored in directory: /private/var/folders/pn/r59j98xn3z30mhhv5_hhh8m80000gn/T/pip-ephem-wheel-cache-ztgj5en7/wheels/c4/4b/16/05aa356d92007c1e0ad97f36a6b05a5361226ff6a0f41edd01
   Successfully built dynvertest
   Installing collected packages: dynvertest
     Attempting uninstall: dynvertest
       Found existing installation: dynvertest 0.0.1689623603
       Uninstalling dynvertest-0.0.1689623603:
         Successfully uninstalled dynvertest-0.0.1689623603
   Successfully installed dynvertest-0.0.1689623616

That version is based on the epoch at installation time, based on
``version = {attr = "dynvertest.dynamicversion"}`` in
``pyproject.toml``. Reinstalling the pacakge will result in a new
package version, based on the epoch at reinstallation time.

Not officially supported?
-------------------------

It’s worth noting that the setuptools has `an official answer for
this <https://setuptools.pypa.io/en/latest/userguide/pyproject_config.html#attr>`__:

   ``attr`` is meant to be used when the module attribute is statically
   specified (e.g. as a string, list or tuple). As a rule of thumb, the
   attribute should be able to be parsed with
   ```ast.literal_eval()`` <https://docs.python.org/3/library/ast.html#ast.literal_eval>`__,
   and should not be modified or re-assigned.

This seems to say that only literals like numbers or strings are
supported. ``ast.literal_eval()`` will not run a function. In practice,
though, this doesn’t seem to be what setuptools actually uses to handle
dynamic versions in ``pyproject.toml``.

What’s it doing in the source code
----------------------------------

In
`config/expand.py <https://github.com/pypa/setuptools/blob/main/setuptools/config/expand.py#L194>`__,
we can see:

.. code:: python3

       try:
           return getattr(StaticModule(module_name, spec), attr_name)
       except Exception:
           # fallback to evaluate module
           module = _load_spec(spec, module_name)
           return getattr(module, attr_name)

The docstring for that function says

   This function will try to read the attributed statically first (via
   :func:``ast.literal_eval``), and only evaluate the module if it
   fails.

So it’s specifically built to do this, but it’s not the preferred way.

Used in previous versions with setup.cfg
----------------------------------------

When progfiguration was first written, it relied on setup.cfg’s support
for dynamic versions. The build script added a version file, and the
dynamic version would import that file and return the version it
defined, and return a fallback version on import error.

When I wanted to update it to use ``pyproject.toml`` only, I found the
footnote quoted above from the setuptools documentation which claimed it
isn’t possible.

I plan to keep using it, at least for now, even if it isn’t supported,
but only in my progfigsite package. Using it isn’t part of the core
progfiguration package, and your own progfigsite package(s) can use
whatever method you like.

Why is this useful?
-------------------

It is useful in progfigsite repositories because it allows date-based
versioning at build time. When writing system configuration, it’s useful
to be able to make a change and deploy it iteratively very quickly. We
want to avoid toil from updating a version file between each cycle.

Alternatives to setuptools?
---------------------------

Note that this is not ``pyproject.toml`` support, it’s setuptools
support. Other build backends might support it officially, or might not
support it.

According to `this
report <https://stackoverflow.com/questions/70272023/using-pyproject-toml-with-flexible-version-from-datetime>`__,
`Flit <https://flit.pypa.io/en/latest/index.html>`__ allows dynamic
version functions as well, but Flit’s documentation doesn’t specifically
claim support.

See also
--------

-  `Single-sourcing the package
   version <https://packaging.python.org/en/latest/guides/single-sourcing-package-version/>`__
