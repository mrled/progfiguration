To do
=====

* Add a "tricks" section of the docs
    * Dynamic module lookup (sitewraper.py)
        * How sitewrapper works and what it's for
        * Importing a package from a filesystem path
        * The old ``progfiguration_build.py`` script, which could be called from CI and was also imported by path insite progfiguration_cli
          (since deprecated since lobotomy and moving to progfigbuild; see git history)

    * zipapp
    * Packages with just pyproject.toml
    * run() command which outputs to stderr/stdout and also captures them
    * Dynamic version trickery
    * Data files in the Python stdlib: json, csv, configfile, and even TOML in Python 3.11+, also TOML in recent pip and setuptools
      (h/t <https://til.simonwillison.net/python/pyproject>)
    * Ode to Python stdlib
        * Data files (per above)
        * unittest module is good enough to start with
        * When do we allow dependencies?
          When it's best practice, and supported by well regarded orgs, like requests and setuptools.
          We are more tolerant of dev- and build- time dependencies,
          but runtime dependencies are not permitted in progfiguration core for maximum flexibility.
          Progfigsite implementations can use dependencies whenever it makes sense for them.

    * Vendoring (implementation TBD)
    * Python string.template, including custom subclasses
        * Can you avoid a full featured templating dependency like jinja?
          I do miss conditionals, but...

    * ... all the other tricks I found to make this work

* Add a "lore" section of the docs

  Lore is the most important part of any project.
    * History:
        * Built for psyopsOS
        * Made more general
        * Lobotomized into core and progfigsite

          Progfiguration was originally written as a Python package to manage one set of infrastructure (mine).
          During the lobotomization process,
          we split its brain into two:

          1. core progfiguration, containing generic code that anyone can use, and
          2. site progfiguration, which is different for each site

          For those familiar with other config management systems,
          the Ansible project is to a given organization's ansible repository as core progfiguration is to site progfiguration.

          TODO: Link to pre- and post- lobotomization git commits for context.

* Make sure progfiguration core works on all in-support Python 3 verions
* Currently ``progfiguration build pyz ...`` copies the running progfiguration into the file.
  Consider adding support for downloading a fresh copy from pypi,
  in case the user does something weird with their current version.

* Make the inventory an API.
    Previously, the inventory was a YAML document.
    Now, it is expected to be parsable by ``configparser``, which allows us
    to use just the standard library.
    In the future, define an inventory abstract class, and allow the progfigsite to implement it.
    Provide an easy to use configparser implementation

    That would let the progfigsite depend on any format it wants, including:
        - YAML, which I still prefer over most options
        - configparser format, built in to Python
        - JSON, which is a pain to use but built in to Python
        - Raw Python, which has a nice alignment with the raw Python node/group modules
        - TOML, which is built in to Python 11, and also into pip which is ubiquitous even on older Python versions
        - Some external program that generates any of the above -- especially JSON
        - ... whatever

    This implements our values of keeping the core progfiguration module
    simple, free of dependencies, and easy for sites to extend.

* Make encryption extensible
  * Allow sites to implement their own secrets management, encryption, etc.

* Can I make sphinx-autobuild faster? Waiting 5+ seconds on every single file save is _horrible_.

* Add a philosophy section, or include all of this in the design section:
    * The Python stdlib is one of its strengths, how can we stay within it as much as possible
        * Reference the section in "tricks", or just m ove that stuff here

* Find a way to automatically link functions to their code implementation.
  I really liked this from pdoc.
  I think some Sphinx themes have it?

* Be precise when talking about pulling in other code.
  There's "vendoring", which is copying code into your own project,
  and there's "inlining" or something else,
  which is copying a dependency into a package at build time, like static linking.

* Refer to zipapp/pyz consistently everywhere

* Add support for calling APIs from the controller.
  When we need to do something like create Route53 records,
  there is no host to deploy the package to,
  but we should be able to run it on the controller.

*   Contrast *declarativity* with *idempotency*.

    Idempotency is important in system,
    but you don't need a declarative document to achieve it.
    * Ansible examples that show that declarativity isn't enough...

      You always need to ensure a service is started when the role is done,
      but if you changed any files,
      you need to stop it first.
      A truly declarative system would not concern itself with restarts.

    * When you use Ansible escape hatches into imperativity like ``shell`` tasks
      or writing your own modules,
      you have to ensure idempotency yourself.
