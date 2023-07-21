"""Site configuration goes here

This includes everything that is not generic to how progfiguration works,
but is specific to my hosts/roles/groups/functions/etc.
"""

site_name = "example_site"
site_description = "This site is bundled with progfiguration core as an example"


def mint_version() -> str:
    """Mint a new version number

    This function is called by progfiguration core to generate a version number.
    It may be called by site-specific code as well.
    It should return a string that is a valid pip version number.
    (If you are also building other packages like RPMs,
    make sure to use a version number that is valid for all of them.)
    """
    from datetime import datetime

    dt = datetime.utcnow()
    epoch = int(dt.timestamp())
    version = f"1.0.{epoch}"
    return version


def get_version() -> str:
    """Dynamically get the package version

    If we have version data injected at build time, retrieve that.
    Otherwise return a default version.

    The default version can be any valid version that conforms to your normal versioning scheme.
    A reasonable default is "0.0.1a0".
    """

    try:
        from example_site.builddata import version

        return version.version
    except ImportError:
        return "0.0.1a0"
