"""The root module for the progfigsite package.

Should not reference progfiguration core.
"""


site_name = "nnss_progfigsite"

# What a boring motto.
# From the Wikipedia page for Nevada Test and Training Range (military unit)
site_description = "Force for Freedom"


def get_version() -> str:
    """Dynamically get the package version."""
    try:
        from nnss_progfigsite.builddata import version as builddata_version

        return builddata_version.version
    except Exception as exc:
        return "0.0.1a0"
