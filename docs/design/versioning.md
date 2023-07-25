# Versioning progfiguration and progfigsite packages

Progfiguration is versioned directly,
by setting a version in pyproject.toml.

Progfigsite packages are versioned dynamically,
by exporting a `mint_version() -> str` function in the package root.

`progfiguration build` will run that function to mint a new version number,
and then record it into the package it builds.

When a package is built from `progfiguration build`,
the progfigsite version is used as the package version;
the version of progfiguration core is not part of the package version at all.
If it were, you would not be able to download progfiguration core in a new version of the progfigsite package.

## Improvements

* TODO: add example `mint_version()` that expects a build number from CI
* TODO: add example `mint_version()` that pulls a git revision
