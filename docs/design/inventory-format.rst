Inventory format
================

Previously, the inventory was a YAML document.

Now, it is expected to be parsable by ``configparser``, which allows us
to use just the standard library.

In the future, define an inventory abstract class, and allow the
progfigsite to implement it. That would let the progfigsite depend on
any format it wants, including:

-  YAML, which I still prefer over most options
-  configparser format, built in to Python
-  JSON, which is a pain to use but built in to Python
-  Raw Python, which has a nice alignment with the raw Python node/group
   modules
-  TOML, which is built in to Python 11, and also into pip which is
   ubiquitous even on older Python versions
-  Some external program that generates any of the above – especially
   JSON
-  … whatever

This implements our values of keeping the core progfiguration module
simple, free of dependencies, and easy for sites to extend.

TODO: define an inventory abstract class, and give examples for
TOML/YAML/whatever
