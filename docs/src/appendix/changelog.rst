Changelog
=========

WIP
---

... nothing yet ...

`0.0.10`
--------

- Add progfigsite inventory module
- Remove requirement for progfigsite version module
- Use src-layout for all packages (site and core)
- Remove the ``localhost.localusers`` module (sites can implement this themselves)
- Fix issues with missing package-data
- Add recursive chowns to localhost module
- Fix bug preventing role argument collection in some cases
- Add several tests
- Improve magicrun logging
- Fix many miscellaneous bugs and typos
- Improve documentation
- Remove dead code

`0.0.9`
-------

* Require site packages to have a ``version`` submodule with a ``get_versio()`` function
* Configure logging in all tests
* Allow reconfiguring logging without duplicate handlers

`0.0.8`
-------

* Simplify the API for progfigsites, including the root module and the cli shim
* Add ``sitehelpers`` module, move inventory implementations there
* Separate ``hosts_conf()`` and ``secrets_conf()`` helper functions
* Make progfigsite shim easier to understand
* Add tests
* Documentation improvements

`0.0.7`
-------

* Fix bugs when running sites in some states
* Replace progfiguration.progfigsite_module_path  with sitewrapper ``get_`` and ``set_`` methods
* Require sites to call ``sitewrapper.set_progfigsite_by_module_name()`` in their root module

`0.0.6`
-------

* Make API that progfigsites have to implement simpler
* Improve test coverage
* Make secret and host storage for inventory pluggable
* Update and expand documentation
* Add sitedata concept for site-specific node data
* Accept arguments to configure secret store on the commandline

`0.0.5`
-------

* Clean up ``InventoryNode`` class from leftover coupling to psyopsOS

`0.0.4`
-------

* Use PyInvoke for development.
* Add analytics to the docs site.
* Make role reference arguments extensible.
  This will enable extensible Inventory configuration and encryption systems in the future.
* Remove Bunch and just use the simple dict.
* Fix various bugs.

`0.0.3`
-------

* Add ``progfiguration newsite`` command for creating a new site
* Improve new user documentation

`0.0.2`
-------

* Fix vendored progfiguration error
* Fix progfigsite package names for zipapp
* Remove old dynamic argparse ``__doc__``  strings from commands
  (this is handled by Sphinx now)
* Have docs retrieve version from the package metadata
* Documentation improvements

`0.0.2a8`
---------

* Improve documentation
* Minor bugfixes

`0.0.2a7`
---------

* In magicrun, get any output after the process closed

`0.0.2a6`
---------

* Fix bug causing Inventory exception

`0.0.2a5`
---------

* Improve documentation
* Remove old dependencies

`0.0.2a4`
---------

* Add a LICENSE
* Improve documentation
* Use Sphinx for documentation

`0.0.2a3`
---------

* Support all features from pre-lobotomy progfiguration
