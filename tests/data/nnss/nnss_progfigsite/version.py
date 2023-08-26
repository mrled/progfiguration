"""A get_version() function.

get_version() used to get the current package version,
at both runtime and build time.

It must return the correct value in multiple contexts:

building a package (e.g. with `python -m build`)
    First look for ``progfigsite.builddata.version``,
    which will have been injected at build time by
    `progfiguration.progfigbuild.ProgfigsitePythonPackagePreparer`.
    If that fails, fall back to the default value returned by this function,

installing from a built package (e.g. a .tar.gz or .whl)
    Use ``progfigsite.builddata.version`` as above.
    This should always be present for a built package.

installing from source (e.g. with `pip install -e .`)
    Use the default value returned by this function,
    which a very low version number.
    ``progfigsite.builddata.version`` should never be present in this case.

The default version should be very low.
"""


def get_version() -> str:
    """Dynamically get the package version."""
    try:
        from progfiguration import sitewrapper

        builddata_version = sitewrapper.site_submodule("builddata.version")
        return builddata_version.version
    except Exception as exc:
        return "0.0.1a0"
