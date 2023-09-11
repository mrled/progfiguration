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
        from progfiguration import sitewrapper

        builddata_version = sitewrapper.site_submodule("builddata.version")
        return builddata_version.version
    except Exception as exc:
        return "0.0.1a0"
