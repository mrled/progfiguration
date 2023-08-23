"""Default versioning for progfiguration sites"""


from datetime import datetime

from progfiguration import sitewrapper


def mint_version_factory_from_epoch(major: int = 1, minor: int = 0):
    """Return a mint_version() function.

    mint_version() is called by progfiguration core to generate a version number,
    and it may be called by site-specific code as well.
    It should return a string that is a valid pip version number.

    For sites that are also building other packages like RPMs,
    it is important to use a version number that is valid for all of them.

    This function returns a function that can be used as mint_version().
    The version number is based on the current time,
    in the format 1.0.<seconds since the epoch>.
    """

    def mint_version() -> str:
        """Mint a new version number"""
        dt = datetime.utcnow()
        epoch = int(dt.timestamp())
        version = f"{major}.{minor}.{epoch}"
        return version

    return mint_version


def get_version_factory_with_simple_fallback(default_version: str = "0.0.1a0"):
    """Return a get_version() function.

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
            builddata_version = sitewrapper.site_submodule("builddata.version")
            return builddata_version.version
        except Exception as exc:
            return default_version

    return get_version
