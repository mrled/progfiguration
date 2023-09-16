"""The root module for the progfigsite package.

Should not reference progfiguration core.
"""


site_name = "example_site"
"""The name of the site package

This must match the name of the site package defined in pyproject.toml.
"""

site_description = "This site is bundled with progfiguration core as an example"
"""The description of the site"""


def get_version() -> str:
    """Dynamically get the package version."""
    try:
        from example_site.builddata import version as builddata_version

        return builddata_version.version
    except Exception as exc:
        return "0.0.1a0"
