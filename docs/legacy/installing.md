# Installing progfiguration

Progfiguration is installed by vendoring it.

## Initial installation

* Copy the contents of this repo into an empty folder in your project
* Customize the `progfiguration/site/` directory.
    * Add your hosts and functions to `inventory.yml`
    * Add node and group files under `nodes/` and `groups/`
    * Create roles under `roles/`
    * Encrypt secrets with `progfiguration encrypt ...`
    * Add any custom code to `sitelib/`
* You can customize vendored progfiguration code outside of the `site/` directory,
  but it will make upgrading more error prone.
  See below.
    * Ideally, you will not need to make any chages.
    * The functionality is there if you need it.
    * Consider filing a bug against progfiguration if there is a missing extension point that would have allowed you to do what you needed in `site/`

## Upgrading

* Copy the contents of this repo into an empty folder on your host
* Make sure you haven't changed any files with a diff command (TODO: put something useful here)
    * If you have made changes, make note of them and reimplement them in the new version
* Read the changelog to learn of any breaking changes,
  and adjust your `site/` code to handle them appropriately.

## Rationale

This is a low-sophistication approach that provides these benefits:

* Maximum flexibility for users;
  you can do anything you want,
  as long as you're willing to maintain it when upgrading the core progfiguration code
* Repositories and packages are self-contained.
  * While this is exactly the shape of problem that packaging systems (like pip) were invented for,
    keeping progfiguration in a generic pip package
    means the site package would have to depend on the core package,
    which means that applying state requires managing two pacakges.
  * This enables the fast zip file deployment method,
    which doesn't understand dependencies.

## Security implications

The behavior of progfiguration core will certainly have security implications,
as it is configuration management code.

This is one reason to avoid modifying core progfiguration code.

It's also one reason we keep core progfiguration code small.
The less code we ship, the less code could need an urgent upgrade.

If you maintain modifications to core progfiguration code
and cannot upgrade when a security update is released,
you may need to backport the changes yourself,
or verify that they do not affect you.

## Progfiguration's commitments

* Maintain a useful stable API that sites can call
* Document deprecations of the stable API
* Provide tools for comparing any vendored copy with upstream

## When changing vendored progfiguration core

* Be judicious.
  Add or change just one thing at a time,
  so that it's easy to understand what's different.
* Provide lots of documentation in comments.
  You'll have to port this code to each new version of progfiguration yourself.
