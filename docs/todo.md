# Todo

* Add a "tricks" section of the docs
    * Dynamic module lookup (sitewraper.py)
        * How sitewrapper works and what it's for
        * Importing a package from a filesystem path
        * The old `progfiguration_build.py` script, which could be called from CI and was also imported by path insite progfiguration_cli
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
    * ... all the other tricks I found to make this work
* Add a "lore" section of the docs
    * History:
        * Built for psyopsOS
        * Made more general
        * Lobotomized into core and progfigsite
* Make sure progfiguration core works on all in-support Python 3 verions
