# Lobotomization

Progfiguration was originally written as a Python package to manage one set of infrastructure (mine).
During the lobotomization process,
we split its brain into two:

1. core progfiguration, containing generic code that anyone can use, and
2. site progfiguration, which is different for each site

For those familiar with other config management systems,
the Ansible project is to a given organization's ansible repository as core progfiguration is to site progfiguration.

## Lobotomization todo:

* Create an example site directory
* Re-base psyops progfiguration site repo on this repo
* Scrub references to psyops from this repo
* Organize documentation so that it makes sense when vendored
* Instead of installing multiple scripts as `console_scripts`,
  provide a `site` subcommand and allow installing site-specific functionality
  as sub-sub-commands there.
* Maintain a progfiguration verion separate from the site version,
  and report them to the user in a way that makes sense.
    * Probably the progfiguration version should _not_
      be part of the site configuration package version,
      because if it were, users could never downgrade.
    * Move/update version.py in this repo in the process
* Write documentation
    * Provide pydoc for everything in progfiguration core
    * Document the modules more generally,
      why is certain functionality included/excluded
    * Document philosophy
    * Add a getting-started example
* Build a site for progfiguration core, its prose documentation, and its pydoc
* Can I have it work without vendoring?
  Build process downloads core from pip and includes it in zip?
  This would allow users that don't need to customize core to work without vendoring and manual updates.
    * Use 2 packages: `progfiguration` for core, and `progfiguration_site` for site.
