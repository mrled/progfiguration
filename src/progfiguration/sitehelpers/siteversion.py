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
