# Lobotomization

Progfiguration was originally written as a Python package to manage one set of infrastructure (mine).
During the lobotomization process,
we split its brain into two:

1. core progfiguration, containing generic code that anyone can use, and
2. site progfiguration, which is different for each site

For those familiar with other config management systems,
the Ansible project is to a given organization's ansible repository as core progfiguration is to site progfiguration.

## Lobotomization todo:

* Re-base psyops progfiguration site repo on this repo
* Organize documentation so that it makes sense when vendored
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
