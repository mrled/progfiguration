"""Site configuration goes here

This includes everything that is not generic to how progfiguration works,
but is specific to my hosts/roles/groups/functions/etc.
"""

site_name = "Nevada Test Site"

# What a boring motto.
# From the Wikipedia page for Nevada Test and Training Range (military unit)
site_description = "Force for Freedom"


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
