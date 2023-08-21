"""Site configuration goes here

This includes everything that is not generic to how progfiguration works,
but is specific to my hosts/roles/groups/functions/etc.
"""

from progfiguration import sitewrapper
from progfiguration.inventory.storeimpl.invconf import inventory_conf


site_name = "example_site"
"""The name of the site package

This must match the name of the site package defined in pyproject.toml.
"""

site_description = "This site is bundled with progfiguration core as an example"
"""The description of the site"""

# The progfigsite package must be set before calling anything else from progfiguration core.
sitewrapper.set_progfigsite_by_module_name(site_name)

# Use progfiguration core to create an inventory
hoststore, secretstore = inventory_conf(sitewrapper.site_submodule_resource("", "inventory.conf"))


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

    In pyproject.toml, this function is used to set the package version.
    That means it must return the correct value in multiple contexts.

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
    """

    try:
        from example_site.builddata import version  # type: ignore

        return version.version
    except Exception as exc:
        default_version = "0.0.1a0"
        return default_version
