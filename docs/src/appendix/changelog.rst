Changelog
=========

WIP
---

... nothing yet ...

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
